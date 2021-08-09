import pytest

from app.config import get_settings
from app.main import app

TEST_UUID = "64cabc63-7b60-46b6-89de-4405265ff51b"

settings = get_settings()


def test_create_user(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    assert response.json()["email"] == payload["email"]
    assert response.json()["full_name"] == payload["full_name"]
    assert response.json()["id"]


@pytest.mark.parametrize(
    "payload, status_code, detail",
    [
        [
            {
                "email": "missing@mail.com",
                "full_name": "Missing Field",
                "password": "secret",
            },
            422,
            {
                "loc": ["body", "username"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
        [
            {
                "username": "missing",
                "full_name": "Missing Field",
                "password": "secret",
            },
            422,
            {
                "loc": ["body", "email"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
        [
            {
                "username": "missing",
                "email": "missing@mail.com",
                "full_name": "Missing Field",
            },
            422,
            {
                "loc": ["body", "password"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
    ],
)
def test_create_user_missing_field(test_client_with_db, payload, status_code, detail):
    response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert response.status_code == status_code
    assert response.json()["detail"][0] == detail


def test_create_user_invalid_json(test_client_with_db):
    response = test_client_with_db.post(url=app.url_path_for("create_user"), json={})
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", "username"], "msg": "field required", "type": "value_error.missing"},
        {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"},
        {"loc": ["body", "password"], "msg": "field required", "type": "value_error.missing"},
    ]
    response = test_client_with_db.post(
        url=app.url_path_for("create_user"),
        json={"username": "test_user", "email": "testemail", "full_name": "Test User", "password": "secret"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0] == {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "type": "value_error.email",
    }


def test_read_me(test_client_with_db, create_test_user, issued_test_token):
    test_user = create_test_user.json()
    response = test_client_with_db.get(
        url=app.url_path_for("read_me"),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == test_user["username"]
    assert response.json()["email"] == test_user["email"]
    assert response.json()["full_name"] == test_user["full_name"]


def test_read_my_summaries(test_client_with_db, create_test_user, issued_test_token, create_test_summary):
    response = test_client_with_db.get(
        url=app.url_path_for("read_my_summaries"),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert response.status_code == 200
    # One summary added by create_test_summary fixture.
    assert len(response.json()) == 1


def test_read_my_summaries_not_found(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    new_user_response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert new_user_response.status_code == 201
    authorization = test_client_with_db.post(
        url=app.url_path_for("issue_access_token"),
        data={"username": payload["username"], "password": payload["password"]},
    )
    tokens = authorization.json()
    token_for_new_user = tokens["access_token"]
    response = test_client_with_db.get(
        url=app.url_path_for("read_my_summaries"),
        headers={"Authorization": f"Bearer {token_for_new_user}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Summaries not found"


def test_read_user(test_client_with_db, create_test_user):
    test_user = create_test_user.json()
    response = test_client_with_db.get(url=app.url_path_for("read_user", id=test_user["id"]))
    assert response.status_code == 200
    assert response.json() == {
        "id": test_user["id"],
        "username": test_user["username"],
        "email": test_user["email"],
        "full_name": test_user["full_name"],
    }


def test_read_user_incorrect_id(test_client_with_db):
    response = test_client_with_db.get(url=app.url_path_for("read_user", id=TEST_UUID))
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_all_users(test_client_with_db, create_test_user):
    test_user = create_test_user.json()
    response = test_client_with_db.get(url=app.url_path_for("read_all_users"))
    assert response.status_code == 200
    assert len(list(filter(lambda u: u["id"] == test_user["id"], response.json()))) == 1


def test_update_user(test_client_with_db, create_test_user, issued_test_token):
    test_user = create_test_user.json()
    payload = {
        "username": "update_test_user",
        "email": "update_test_user@mail.com",
        "full_name": "Updated Test User",
        "password": "new_secret",
    }
    unauthorized_response = test_client_with_db.put(
        url=app.url_path_for("update_user", id=test_user["id"]),
        json=payload,
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.put(
        url=app.url_path_for("update_user", id=test_user["id"]),
        json=payload,
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 200
    assert authorized_response.json() == {
        "id": test_user["id"],
        "username": payload["username"],
        "email": payload["email"],
        "full_name": payload["full_name"],
    }


@pytest.mark.parametrize(
    "user_id, payload, status_code, detail",
    [
        [
            TEST_UUID,
            {
                "username": "update_test_user",
                "email": "update_test_user@mail.com",
                "full_name": "Updated Test User",
                "password": "new_secret",
            },
            404,
            "User not found",
        ],
        [
            TEST_UUID,
            {"email": "updated_email"},
            422,
            [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ],
        ],
    ],
)
def test_update_user_invalid(
    test_client_with_db, create_test_user, issued_test_token, user_id, payload, status_code, detail
):
    unauthorized_response = test_client_with_db.put(
        url=app.url_path_for("update_user", id=user_id),
        json=payload,
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.put(
        url=app.url_path_for("update_user", id=user_id),
        json=payload,
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == status_code
    assert authorized_response.json()["detail"] == detail


def test_update_user_without_rights(test_client_with_db, create_test_user, issued_test_token):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    new_user_response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert new_user_response.status_code == 201
    new_user = new_user_response.json()
    payload = {
        "username": "update_test_user",
        "email": "update_test_user@mail.com",
        "full_name": "Updated Test User",
        "password": "new_secret",
    }
    not_owner_response = test_client_with_db.put(
        url=app.url_path_for("update_user", id=new_user["id"]),
        json=payload,
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert not_owner_response.status_code == 403
    assert not_owner_response.json()["detail"] == "Insufficient rights to update this user"


def test_delete_user(test_client_with_db, create_test_user, issued_test_token):
    test_user = create_test_user.json()
    unauthorized_response = test_client_with_db.delete(url=app.url_path_for("delete_user", id=test_user["id"]))
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.delete(
        url=app.url_path_for("delete_user", id=test_user["id"]),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 200
    assert authorized_response.json() == {
        "id": test_user["id"],
        "username": test_user["username"],
        "email": test_user["email"],
        "full_name": test_user["full_name"],
    }


def test_delete_user_without_rights(test_client_with_db, create_test_user, issued_test_token):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    new_user_response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert new_user_response.status_code == 201
    new_user = new_user_response.json()
    not_owner_response = test_client_with_db.delete(
        url=app.url_path_for("delete_user", id=new_user["id"]),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert not_owner_response.status_code == 403
    assert not_owner_response.json()["detail"] == "Insufficient rights to delete this user"


def test_delete_user_incorrect_id(test_client_with_db, create_test_user, issued_test_token):
    unauthorized_response = test_client_with_db.delete(url=app.url_path_for("delete_user", id=TEST_UUID))
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.delete(
        url=app.url_path_for("delete_user", id=TEST_UUID),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 404
    assert authorized_response.json()["detail"] == "User not found"
