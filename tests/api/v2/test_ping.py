from .conftest import app


def test_ping(test_app):
    response = test_app.get(app.url_path_for(name="pong"))
    assert response.status_code == 200
    assert response.json() == {
        "ping": "pong!",
        "testing": True,
        "environment": "dev",
    }
