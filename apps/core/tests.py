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
