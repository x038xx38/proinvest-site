import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url", "status"),
    [
        ("/", 200),
        ("/robots.txt", 200),
        ("/sitemap.xml", 200),
        ("/admin/login/", 200),
        ("/cms/login/", 200),
    ],
)
def test_smoke(client, url, status):
    assert client.get(url).status_code == status


@pytest.mark.django_db
def test_robots_closed_outside_production(client):
    assert "Disallow: /" in client.get("/robots.txt").content.decode()


@pytest.mark.django_db
def test_header_and_footer_render_navigation_defaults(client):
    html = client.get("/").content.decode()
    for text in ["Инвестиционный подбор", "О проекте", "Контакты", "Политика конфиденциальности"]:
        assert text in html
    assert 'href="#consultation"' in html
    assert 'id="consultation-modal"' in html


@pytest.mark.django_db
def test_styleguide_hidden_from_anonymous(client):
    assert client.get("/styleguide/").status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/styleguide/", "/styleguide/home/", "/styleguide/service/"])
def test_styleguide_renders_for_staff(admin_client, url):
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "Вопросы и ответы" in response.content.decode()


@pytest.mark.django_db
def test_styleguide_unknown_slug(admin_client):
    assert admin_client.get("/styleguide/nope/").status_code == 404


@pytest.mark.django_db
def test_link_block_prefers_page_over_url():
    from wagtail.models import Page

    from apps.core.blocks import LinkBlock

    home = Page.objects.get(depth=2)
    value = LinkBlock().to_python({"text": "Главная", "page": home.pk, "url": "/other/"})
    assert value.href == home.url
    assert LinkBlock().to_python({"text": "Якорь", "page": None, "url": "#faq"}).href == "#faq"


def test_link_block_requires_target():
    from wagtail.blocks.struct_block import StructBlockValidationError

    from apps.core.blocks import LinkBlock, OptionalLinkBlock

    block = LinkBlock()
    with pytest.raises(StructBlockValidationError):
        block.clean(block.to_python({"text": "Куда?", "page": None, "url": ""}))
    optional = OptionalLinkBlock()
    optional.clean(optional.to_python({"text": "", "page": None, "url": ""}))


@pytest.mark.parametrize(
    ("href", "path", "active"),
    [
        ("/uslugi/", "/uslugi/podbor/", True),
        ("/uslugi/", "/kejsy/", False),
        ("/", "/kejsy/", False),
        ("/", "/", True),
        ("#consultation", "/", False),
    ],
)
def test_is_active(href, path, active):
    from apps.core.templatetags.core_tags import is_active

    assert is_active(href, path) is active
