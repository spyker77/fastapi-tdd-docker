import pytest

from app.background.tasks import celery_generate_summary
from app.config import get_settings
from app.main import app
from app.tests.conftest import TEST_USER

TEST_UUID = "64cabc63-7b60-46b6-89de-4405265ff51b"

settings = get_settings()


@pytest.mark.asyncio
async def test_create_user(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert response.status_code == 201
        assert response.json()["username"] == payload["username"]
        assert response.json()["email"] == payload["email"]
        assert response.json()["full_name"] == payload["full_name"]
        assert response.json()["id"]


@pytest.mark.asyncio
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
async def test_create_user_missing_field(test_client_with_db, payload, status_code, detail):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert response.status_code == status_code
        assert response.json()["detail"][0] == detail


@pytest.mark.asyncio
async def test_create_user_invalid_json(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json={})
        assert response.status_code == 422
        assert response.json()["detail"] == [
            {"loc": ["body", "username"], "msg": "field required", "type": "value_error.missing"},
            {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"},
            {"loc": ["body", "password"], "msg": "field required", "type": "value_error.missing"},
        ]

        response = await client.post(
            url=app.url_path_for("create_user"),
            json={"username": "test_user", "email": "testemail", "full_name": "Test User", "password": "secret"},
        )
        assert response.status_code == 422
        assert response.json()["detail"][0] == {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email",
        }


@pytest.mark.asyncio
async def test_read_me(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        test_user = response.json()

        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        response = await client.get(
            url=app.url_path_for("read_me"),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == test_user["id"]
        assert response.json()["username"] == test_user["username"]
        assert response.json()["email"] == test_user["email"]
        assert response.json()["full_name"] == test_user["full_name"]


@pytest.mark.asyncio
async def test_read_my_summaries(test_client_with_db, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)

    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://lipsum.com/"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )

        response = await client.get(
            url=app.url_path_for("read_my_summaries"),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_read_my_summaries_not_found(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    async with test_client_with_db as client:
        new_user_response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert new_user_response.status_code == 201

        authorization = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": payload["username"], "password": payload["password"]},
        )
        tokens = authorization.json()
        token_for_new_user = tokens["access_token"]
        response = await client.get(
            url=app.url_path_for("read_my_summaries"),
            headers={"Authorization": f"Bearer {token_for_new_user}"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Summaries not found"


@pytest.mark.asyncio
async def test_read_user(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        test_user = response.json()

        response = await client.get(url=app.url_path_for("read_user", id=test_user["id"]))
        assert response.status_code == 200
        assert response.json() == {
            "id": test_user["id"],
            "username": test_user["username"],
            "email": test_user["email"],
            "full_name": test_user["full_name"],
        }


@pytest.mark.asyncio
async def test_read_user_incorrect_id(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.get(url=app.url_path_for("read_user", id=TEST_UUID))
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_read_all_users(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        test_user = response.json()

        response = await client.get(url=app.url_path_for("read_all_users"))
        assert response.status_code == 200
        assert len(list(filter(lambda u: u["id"] == test_user["id"], response.json()))) == 1


@pytest.mark.asyncio
async def test_update_user(test_client_with_db):
    payload = {
        "username": "update_test_user",
        "email": "update_test_user@mail.com",
        "full_name": "Updated Test User",
        "password": "new_secret",
    }
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        test_user = response.json()

        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.put(
            url=app.url_path_for("update_user", id=test_user["id"]),
            json=payload,
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.put(
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


@pytest.mark.asyncio
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
async def test_update_user_invalid(test_client_with_db, user_id, payload, status_code, detail):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.put(
            url=app.url_path_for("update_user", id=user_id),
            json=payload,
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.put(
            url=app.url_path_for("update_user", id=user_id),
            json=payload,
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == status_code
        assert authorized_response.json()["detail"] == detail


@pytest.mark.asyncio
async def test_update_user_without_rights(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        new_user_response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert new_user_response.status_code == 201

        new_user = new_user_response.json()
        payload = {
            "username": "update_test_user",
            "email": "update_test_user@mail.com",
            "full_name": "Updated Test User",
            "password": "new_secret",
        }
        not_owner_response = await client.put(
            url=app.url_path_for("update_user", id=new_user["id"]),
            json=payload,
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert not_owner_response.status_code == 403
        assert not_owner_response.json()["detail"] == "Insufficient rights to update this user"


@pytest.mark.asyncio
async def test_delete_user(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        test_user = response.json()

        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.delete(url=app.url_path_for("delete_user", id=test_user["id"]))
        assert unauthorized_response.status_code == 401

        authorized_response = await client.delete(
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


@pytest.mark.asyncio
async def test_delete_user_without_rights(test_client_with_db):
    payload = {"username": "new", "email": "new@mail.com", "full_name": "New User", "password": "secret"}
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        new_user_response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert new_user_response.status_code == 201

        new_user = new_user_response.json()
        not_owner_response = await client.delete(
            url=app.url_path_for("delete_user", id=new_user["id"]),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert not_owner_response.status_code == 403
        assert not_owner_response.json()["detail"] == "Insufficient rights to delete this user"


@pytest.mark.asyncio
async def test_delete_user_incorrect_id(test_client_with_db):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.delete(url=app.url_path_for("delete_user", id=TEST_UUID))
        assert unauthorized_response.status_code == 401

        authorized_response = await client.delete(
            url=app.url_path_for("delete_user", id=TEST_UUID),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 404
        assert authorized_response.json()["detail"] == "User not found"
