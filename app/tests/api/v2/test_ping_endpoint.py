from app.main import app


def test_ping(test_client_with_db):
    response = test_client_with_db.get(app.url_path_for("pong"))
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!", "testing": True, "environment": "dev"}
