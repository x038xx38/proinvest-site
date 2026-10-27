import logging

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.models import SiteSettings

from .forms import LeadForm, local_path
from .tasks import notify_new_lead

logger = logging.getLogger(__name__)


@require_POST
def create_lead(request):
    """Приём заявки со всех форм сайта. Fetch получает JSON, обычная отправка — страницу."""
    form = LeadForm(request.POST)
    wants_json = "application/json" in request.headers.get("Accept", "")
    back_url = local_path(request.POST.get("page_url", "")) or "/"

    if not form.is_valid():
        if wants_json:
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        return render(
            request, "leads/result.html", {"form": form, "back_url": back_url}, status=400
        )

    # Боту отвечаем как человеку, чтобы он не подбирал обход
    if not form.is_spam:
        lead = form.save(commit=False)
        lead.page = form.cleaned_data["page_id"]
        lead.consent_at = timezone.now()
        consent_page = SiteSettings.load(request_or_site=request).consent_page
        lead.consent_document = consent_page.url if consent_page else ""
        lead.ip = request.META.get("REMOTE_ADDR") or None
        lead.user_agent = request.headers.get("User-Agent", "")[:300]
        lead.save()
        transaction.on_commit(lambda: queue_notification(lead.pk))

    if wants_json:
        return JsonResponse({"ok": True})
    return render(request, "leads/result.html", {"ok": True, "back_url": back_url})


def queue_notification(lead_id):
    # Заявка уже в базе: недоступность очереди не должна ронять ответ посетителю
    try:
        notify_new_lead.delay(lead_id)
    except Exception:
        logger.exception("Не удалось поставить уведомление о заявке %s в очередь", lead_id)
