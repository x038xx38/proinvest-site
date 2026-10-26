from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Контуры иконок 24×24 в стиле Lucide (ISC). Имена совпадают с blocks.ICON_CHOICES
ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "chart": '<path d="M22 7 13.5 15.5l-5-5L2 17"/><path d="M16 7h6v6"/>',
    "wallet": (
        '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3'
        'a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>'
    ),
    "percent": (
        '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/>'
        '<circle cx="17.5" cy="17.5" r="2.5"/>'
    ),
    "key": (
        '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/>'
        '<path d="m15.5 7.5 3 3L22 7l-3-3"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "document": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>'
    ),
    "users": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "building": (
        '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/>'
        '<path d="M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01'
        'M16 14h.01"/>'
    ),
    "box": (
        '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73'
        'l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/>'
    ),
    "car": (
        '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2'
        "-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4"
        'c0 .6.4 1 1 1h2"/>'
        '<circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>'
    ),
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "map-pin": (
        '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>'
    ),
    "graduation": '<path d="m2 10 10-5 10 5-10 5zM22 10v6"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "arrow-right": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "phone": (
        '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8'
        " 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1"
        "-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2"
        ' 2 0 0 1 22 16.92z"/>'
    ),
    "send": '<path d="m22 2-7 20-4-9-9-4zM22 2 11 13"/>',
}


@register.simple_tag
def icon(name, css_class="size-6"):
    paths = ICONS.get(name, ICONS["check"])
    return format_html(
        '<svg class="{}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>',
        css_class,
        mark_safe(paths),  # константы из ICONS, не пользовательский ввод
    )


@register.filter
def rub(value):
    """620000 → «620 000 ₽» с неразрывными пробелами."""
    if value in (None, ""):
        return ""
    return f"{int(value):,}".replace(",", "\u00a0") + "\u00a0₽"


@register.filter
def is_active(href, path):
    """Пункт меню активен на своей странице и её дочерних (кроме главной и якорей)."""
    if not href or not href.startswith("/"):
        return False
    if href == "/":
        return path == "/"
    return path.startswith(href)
