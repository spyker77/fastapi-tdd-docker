from app.main import app


def test_access_token(test_client_with_db):
    response = test_client_with_db.post(
        url=app.url_path_for("issue_access_token"),
        data={"username": "not_exist", "password": "none"},
    )
    assert response.json()["detail"] == "Incorrect username or password"
