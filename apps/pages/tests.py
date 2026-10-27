import io
import tempfile

import pytest
from django.core.management import call_command
from django.db import transaction
from django.test import override_settings
from wagtail.models import Page

from apps.cases.models import CasePage
from apps.core.blocks import CasesBlock
from apps.core.templatetags.core_tags import rub
from apps.services.models import ServicePage

SITE_URLS = [
    "/",
    "/uslugi/",
    "/uslugi/podbor/",
    "/uslugi/upravlenie/",
    "/o-proekte/",
    "/kejsy/",
    "/kejsy/?tip=kladovaya",
    "/kejsy/?usluga=podbor",
    "/kejsy/?page=99",
    "/kejsy/demo-1/",
    "/stati/",
    "/stati/rubrika/kladovye/",
    "/stati/demo-1/",
    "/kontakty/",
    "/obuchenie/",
    "/politika/",
    "/soglasie/",
    "/oferta/",
]


@pytest.fixture(scope="module")
def _site_tree(django_db_setup, django_db_blocker):
    """Дерево страниц создаётся один раз на модуль и откатывается в конце.

    Фото автора курса сохраняется во временную папку, а не в media/ разработчика.
    """
    with (
        tempfile.TemporaryDirectory() as media_root,
        override_settings(MEDIA_ROOT=media_root),
        django_db_blocker.unblock(),
        transaction.atomic(),
    ):
        call_command("setup_site", demo=True, stdout=io.StringIO())
        yield
        transaction.set_rollback(True)


@pytest.fixture
def site(_site_tree, db):
    pass


@pytest.mark.parametrize("url", SITE_URLS)
def test_pages_render(client, site, url):
    assert client.get(url).status_code == 200


def test_setup_site_is_idempotent(site):
    count = Page.objects.count()
    call_command("setup_site", demo=True, stdout=io.StringIO())
    assert Page.objects.count() == count


def test_course_page_has_waitlist_form_and_author_photo(client, site):
    html = client.get("/obuchenie/").content.decode()
    assert 'name="lead_type" value="course_waitlist"' in html
    assert 'id="predzapis"' in html
    assert "Максим Гурлёв" in html
    assert 'alt="Максим Гурлёв"' in html


def test_forms_link_consent_and_privacy_pages(client, site):
    html = client.get("/kontakty/").content.decode()
    assert 'href="/soglasie/"' in html
    assert 'href="/politika/"' in html


def test_setup_site_keeps_single_author_photo_and_consent_link(site):
    from wagtail.images.models import Image

    from apps.core.models import Navigation

    call_command("setup_site", stdout=io.StringIO())
    assert Image.objects.filter(title="Максим Гурлёв").count() == 1
    urls = [block.value.href for block in Navigation.load().legal_links]
    assert urls.count("/soglasie/") == 1


def test_unknown_blog_category_is_404(client, site):
    assert client.get("/stati/rubrika/nope/").status_code == 404


def test_case_filters(client, site):
    html = client.get("/kejsy/?usluga=upravlenie").content.decode()
    assert "две кладовые" in html
    assert "машино-место у метро" not in html


def test_cases_block_on_service_page_shows_only_its_cases(site):
    service = ServicePage.objects.get(slug="upravlenie")
    value = CasesBlock().to_python({"limit": 3})
    titles = [card["title"] for card in CasesBlock.get_cards(value, service)]
    assert titles == ["Демо: две кладовые под перепродажу"]


def test_cases_block_selected_pages_win(site):
    case = CasePage.objects.get(slug="demo-2")
    value = CasesBlock().to_python({"pages": [case.pk], "limit": 3})
    assert [card["url"] for card in CasesBlock.get_cards(value)] == [case.url]


def test_cms_edit_forms_open(admin_client, site):
    for page in Page.objects.filter(depth__gte=2):
        response = admin_client.get(f"/cms/pages/{page.pk}/edit/")
        assert response.status_code == 200, page.url_path


def test_case_yield_display(site):
    rent = CasePage.objects.get(slug="demo-1")
    resale = CasePage.objects.get(slug="demo-3")
    assert rent.yield_display == "14 % год."
    assert resale.yield_display == "+32 %"


def test_rub():
    assert rub(1900000) == "1 900 000 ₽"
    assert rub(None) == ""
