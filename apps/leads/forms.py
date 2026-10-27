from django import forms
from wagtail.models import Page

from .models import Lead


def local_path(url):
    """Только путь на этом сайте: /uslugi/, но не //example.com и не javascript:."""
    return url if url.startswith("/") and not url.startswith("//") else ""


class LeadForm(forms.ModelForm):
    consent = forms.BooleanField(
        error_messages={"required": "Нужно согласие на обработку персональных данных"}
    )
    page_id = forms.IntegerField(required=False)
    # Ловушка для ботов: поле скрыто от людей, заполненное — заявка не сохраняется
    website = forms.CharField(required=False)

    class Meta:
        model = Lead
        fields = ["lead_type", "name", "contact", "comment", "page_url"]
        error_messages = {
            "name": {"required": "Укажите имя"},
            "contact": {"required": "Укажите телефон или Telegram"},
        }

    def clean_page_url(self):
        return local_path(self.cleaned_data["page_url"])

    def clean_page_id(self):
        page_id = self.cleaned_data["page_id"]
        return Page.objects.filter(pk=page_id).first() if page_id else None

    @property
    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
