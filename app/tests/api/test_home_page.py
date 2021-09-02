from app.main import app


def test_home_page_message(test_client_with_db):
    response = test_client_with_db.get(url=app.url_path_for("home_page_message"))
    assert response.json()["message"] == "Please refer to the /docs or /redoc path to access the API documentation"
