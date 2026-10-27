import pytest
from wagtail.models import Page

from apps.leads import views
from apps.leads.models import Lead
from apps.leads.tasks import notify_new_lead

JSON = {"HTTP_ACCEPT": "application/json"}


@pytest.fixture
def queued(monkeypatch):
    """Перехват постановки письма в очередь: в тестах Redis не нужен."""
    calls = []
    monkeypatch.setattr(views.notify_new_lead, "delay", calls.append)
    return calls


def form_data(**overrides):
    data = {
        "lead_type": "consultation",
        "name": "Анна",
        "contact": "+7 900 000-00-00",
        "comment": "Бюджет 1 млн",
        "consent": "on",
        "page_url": "/uslugi/podbor/",
        "website": "",
    }
    return {**data, **overrides}


@pytest.mark.django_db
def test_lead_saved_and_notification_queued(client, queued, django_capture_on_commit_callbacks):
    home = Page.objects.get(depth=2)
    with django_capture_on_commit_callbacks(execute=True):
        response = client.post("/zayavka/", form_data(page_id=home.pk), **JSON)

    assert response.json() == {"ok": True}
    lead = Lead.objects.get()
    assert (lead.name, lead.contact, lead.lead_type) == ("Анна", "+7 900 000-00-00", "consultation")
    assert lead.status == Lead.Status.NEW
    assert lead.page_id == home.pk
    assert lead.page_url == "/uslugi/podbor/"
    assert lead.consent_at is not None
    assert queued == [lead.pk]


@pytest.mark.django_db
def test_lead_requires_consent_and_contacts(client, queued):
    response = client.post("/zayavka/", form_data(consent="", name="", contact=""), **JSON)

    assert response.status_code == 400
    assert set(response.json()["errors"]) == {"consent", "name", "contact"}
    assert not Lead.objects.exists()


@pytest.mark.django_db
def test_honeypot_answers_ok_but_drops_lead(client, queued):
    response = client.post("/zayavka/", form_data(website="http://spam.example"), **JSON)

    assert response.json() == {"ok": True}
    assert not Lead.objects.exists()
    assert queued == []


@pytest.mark.django_db
def test_form_without_js_gets_result_page(client, queued):
    response = client.post("/zayavka/", form_data(lead_type="course_waitlist"))

    assert response.status_code == 200
    assert "Спасибо, заявка отправлена" in response.content.decode()
    assert Lead.objects.get().lead_type == "course_waitlist"


@pytest.mark.django_db
def test_external_page_url_is_dropped(client, queued):
    response = client.post("/zayavka/", form_data(page_url="//evil.example/", consent=""))

    assert response.status_code == 400
    assert 'href="/"' in response.content.decode()


@pytest.mark.django_db
def test_get_not_allowed(client):
    assert client.get("/zayavka/").status_code == 405


@pytest.mark.django_db
def test_notify_new_lead_sends_email(settings, mailoutbox):
    settings.LEADS_NOTIFY_EMAILS = ["manager@example.com"]
    lead = Lead.objects.create(
        name="Анна", contact="@anna", consent_at="2026-10-27T10:00:00+03:00", page_url="/kontakty/"
    )

    notify_new_lead(lead.pk)

    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.to == ["manager@example.com"]
    assert "Анна" in message.subject
    assert "@anna" in message.body
    assert f"/admin/leads/lead/{lead.pk}/change/" in message.body


@pytest.mark.django_db
def test_lead_admin_pages_open(admin_client):
    lead = Lead.objects.create(name="Анна", contact="@anna", consent_at="2026-10-27T10:00:00+03:00")

    assert admin_client.get("/admin/leads/lead/").status_code == 200
    assert admin_client.get(f"/admin/leads/lead/{lead.pk}/change/").status_code == 200
