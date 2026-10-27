from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Lead


@shared_task(autoretry_for=(SMTPException, OSError), retry_backoff=60, max_retries=5)
def notify_new_lead(lead_id):
    """Письмо о новой заявке на адреса из LEADS_NOTIFY_EMAILS."""
    lead = Lead.objects.filter(pk=lead_id).first()
    if not lead or not settings.LEADS_NOTIFY_EMAILS:
        return
    context = {
        "lead": lead,
        "site_url": settings.WAGTAILADMIN_BASE_URL,
        "admin_url": settings.WAGTAILADMIN_BASE_URL
        + reverse("admin:leads_lead_change", args=[lead.pk]),
    }
    send_mail(
        subject=f"Новая заявка: {lead.get_lead_type_display()} — {lead.name}",
        message=render_to_string("leads/email/new_lead.txt", context),
        from_email=None,
        recipient_list=settings.LEADS_NOTIFY_EMAILS,
    )
