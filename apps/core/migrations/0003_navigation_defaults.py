from django.db import migrations


def link(text, url, children=None):
    value = {"text": text, "page": None, "url": url}
    if children is not None:
        value["children"] = children
    return value


SERVICES = [
    link("Инвестиционный подбор", "/uslugi/podbor/"),
    link("Управление кладовыми и машино-местами", "/uslugi/upravlenie/"),
    link("Обучение", "/obuchenie/"),
]

HEADER_MENU = [
    link("Услуги", "/uslugi/", SERVICES),
    link("О проекте", "/o-proekte/", []),
    link("Кейсы", "/kejsy/", []),
    link("Статьи", "/stati/", []),
    link("Контакты", "/kontakty/", []),
]

FOOTER_COLUMNS = [
    {"title": "Направления", "links": SERVICES},
    {
        "title": "Компания",
        "links": [
            link("О проекте", "/o-proekte/"),
            link("Кейсы", "/kejsy/"),
            link("Статьи", "/stati/"),
            link("Контакты", "/kontakty/"),
        ],
    },
]


def create_navigation(apps, schema_editor):
    Navigation = apps.get_model("core.Navigation")
    if Navigation.objects.exists():
        return
    Navigation.objects.create(
        header_menu=[{"type": "item", "value": item} for item in HEADER_MENU],
        header_button=[{"type": "link", "value": link("Консультация", "#consultation")}],
        footer_columns=[{"type": "column", "value": col} for col in FOOTER_COLUMNS],
        legal_links=[
            {"type": "link", "value": link("Политика конфиденциальности", "/politika/")},
            {"type": "link", "value": link("Оферта", "/oferta/")},
        ],
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0002_navigation")]

    operations = [migrations.RunPython(create_navigation, migrations.RunPython.noop)]
