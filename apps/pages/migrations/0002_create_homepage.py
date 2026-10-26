from django.db import migrations


def create_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("pages.HomePage")
    Locale = apps.get_model("wagtailcore.Locale")

    # Убираем стартовую страницу, которую создаёт Wagtail
    Page.objects.filter(depth=2, slug="home").delete()

    locale = Locale.objects.get_or_create(language_code="ru")[0]
    content_type, _ = ContentType.objects.get_or_create(model="homepage", app_label="pages")
    home = HomePage.objects.create(
        title="Инвестиции в кладовые и машино-места",
        draft_title="Инвестиции в кладовые и машино-места",
        slug="home",
        content_type=content_type,
        path="00010001",
        depth=2,
        numchild=0,
        locale=locale,
        url_path="/home/",
        intro="<p>Подбор, управление и обучение. Санкт-Петербург, Ленинградская область, Москва и Московская область.</p>",
    )
    Page.objects.filter(depth=1).update(numchild=1)
    Site.objects.update_or_create(
        is_default_site=True,
        defaults={"hostname": "localhost", "port": 80, "root_page": home, "site_name": "ПроИнвест"},
    )


def remove_homepage(apps, schema_editor):
    apps.get_model("pages.HomePage").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [migrations.RunPython(create_homepage, remove_homepage)]
