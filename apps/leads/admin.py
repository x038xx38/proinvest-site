from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Lead

STATUS_COLORS = {
    Lead.Status.NEW: "info",
    Lead.Status.IN_PROGRESS: "warning",
    Lead.Status.DONE: "success",
    Lead.Status.SPAM: "danger",
}


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ["name", "contact", "lead_type", "show_status", "page_url", "created_at"]
    list_filter = ["status", "lead_type", "created_at"]
    search_fields = ["name", "contact", "comment"]
    date_hierarchy = "created_at"
    actions = ["mark_in_progress", "mark_done", "mark_spam"]
    fieldsets = [
        (None, {"fields": ["status", "lead_type", "name", "contact", "comment"]}),
        ("Откуда", {"fields": ["page", "page_url", "created_at"]}),
        (
            "Согласие и техданные",
            {"fields": ["consent_at", "consent_document", "ip", "user_agent"]},
        ),
    ]
    readonly_fields = [
        "lead_type",
        "name",
        "contact",
        "comment",
        "page",
        "page_url",
        "created_at",
        "consent_at",
        "consent_document",
        "ip",
        "user_agent",
    ]

    def has_add_permission(self, request):
        return False

    @display(description="Статус", ordering="status", label=STATUS_COLORS)
    def show_status(self, obj):
        return obj.status, obj.get_status_display()

    def set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        self.message_user(request, f"Обновлено заявок: {updated}")

    @admin.action(description="Взять в работу")
    def mark_in_progress(self, request, queryset):
        self.set_status(request, queryset, Lead.Status.IN_PROGRESS)

    @admin.action(description="Отметить обработанными")
    def mark_done(self, request, queryset):
        self.set_status(request, queryset, Lead.Status.DONE)

    @admin.action(description="Отметить как спам")
    def mark_spam(self, request, queryset):
        self.set_status(request, queryset, Lead.Status.SPAM)
