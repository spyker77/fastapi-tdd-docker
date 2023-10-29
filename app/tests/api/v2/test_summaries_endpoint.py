import pytest

from app.background.tasks import celery_generate_summary
from app.config import get_settings
from app.main import app
from app.tests.conftest import TEST_USER

TEST_ID = "0987654321"

settings = get_settings()


@pytest.mark.asyncio
async def test_create_summary(test_client_with_db, monkeypatch):
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

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201
        assert authorized_response.json()["url"] == "https://foo.bar/"


@pytest.mark.asyncio
async def test_create_summaries_invalid_json(test_client_with_db):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 422
        assert authorized_response.json()["detail"][0] == {
            "type": "missing",
            "loc": ["body", "url"],
            "msg": "Field required",
            "input": {},
            "url": "https://errors.pydantic.dev/2.4/v/missing",
        }

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "invalid://url"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 422
        assert authorized_response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"


@pytest.mark.asyncio
async def test_read_summary(test_client_with_db, monkeypatch):
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

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        response = await client.get(url=app.url_path_for("read_summary", id=summary["id"]))
        assert response.status_code == 200
        assert response.json() == {
            "id": summary["id"],
            "url": "https://foo.bar/",
            "summary": "",
            "user_id": summary["user_id"],
        }


@pytest.mark.asyncio
async def test_read_summary_incorrect_id(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.get(url=app.url_path_for("read_summary", id=TEST_ID))
        assert response.status_code == 404
        assert response.json()["detail"] == "Summary not found"


@pytest.mark.asyncio
async def test_read_all_summaries(test_client_with_db, monkeypatch):
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

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        response = await client.get(url=app.url_path_for("read_all_summaries"))
        assert response.status_code == 200
        assert len(list(filter(lambda s: s["id"] == summary["id"], response.json()))) == 1


@pytest.mark.asyncio
async def test_update_summary(test_client_with_db, monkeypatch):
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

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        unauthorized_response = await client.put(
            url=app.url_path_for("update_summary", id=summary["id"]),
            json={"url": "https://updated.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.put(
            url=app.url_path_for("update_summary", id=summary["id"]),
            json={"url": "https://updated.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 200
        assert authorized_response.json() == {
            "id": summary["id"],
            "url": "https://updated.bar/",
            "summary": "",
            "user_id": summary["user_id"],
        }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            TEST_ID,
            {"url": "https://foo.bar"},
            404,
            "Summary not found",
        ],
        [
            TEST_ID,
            {},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "url"],
                    "msg": "Field required",
                    "input": {},
                    "url": "https://errors.pydantic.dev/2.4/v/missing",
                }
            ],
        ],
        [
            TEST_ID,
            {"url": "foo.bar"},
            422,
            [
                {
                    "type": "url_parsing",
                    "loc": ["body", "url"],
                    "msg": "Input should be a valid URL, relative URL without a base",
                    "input": "foo.bar",
                    "ctx": {"error": "relative URL without a base"},
                    "url": "https://errors.pydantic.dev/2.4/v/url_parsing",
                }
            ],
        ],
    ],
)
async def test_update_summary_invalid(test_client_with_db, summary_id, payload, status_code, detail):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.put(
            url=app.url_path_for("update_summary", id=summary_id),
            json=payload,
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.put(
            url=app.url_path_for("update_summary", id=summary_id),
            json=payload,
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == status_code
        assert authorized_response.json()["detail"] == detail


@pytest.mark.asyncio
async def test_update_summary_invalid_url(test_client_with_db):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.put(
            url=app.url_path_for("update_summary", id=TEST_ID),
            json={"url": "invalid://url"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.put(
            url=app.url_path_for("update_summary", id=TEST_ID),
            json={"url": "invalid://url"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 422
        assert authorized_response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"


@pytest.mark.asyncio
async def test_update_summary_without_rights(test_client_with_db, monkeypatch):
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

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        payload = {
            "username": "not_owner",
            "email": "not_owner@mail.com",
            "full_name": "Not Owner",
            "password": "secret",
        }
        not_owner_response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert not_owner_response.status_code == 201

        authorization = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": payload["username"], "password": payload["password"]},
        )
        tokens = authorization.json()
        token_for_not_owner = tokens["access_token"]
        not_owner_response = await client.put(
            url=app.url_path_for("delete_summary", id=summary["id"]),
            json={"url": "https://updated.bar"},
            headers={"Authorization": f"Bearer {token_for_not_owner}"},
        )
        assert not_owner_response.status_code == 403
        assert not_owner_response.json()["detail"] == "Insufficient rights to update this summary"


@pytest.mark.asyncio
async def test_delete_summary(test_client_with_db, monkeypatch):
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

        unauthorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
        )
        assert unauthorized_response.status_code == 401

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        unauthorized_response = await client.delete(url=app.url_path_for("delete_summary", id=summary["id"]))
        assert unauthorized_response.status_code == 401

        authorized_response = await client.delete(
            url=app.url_path_for("delete_summary", id=summary["id"]),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 200
        assert authorized_response.json() == {
            "id": summary["id"],
            "url": "https://foo.bar/",
            "summary": "",
            "user_id": summary["user_id"],
        }


@pytest.mark.asyncio
async def test_delete_summary_without_rights(test_client_with_db, monkeypatch):
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

        authorized_response = await client.post(
            url=app.url_path_for("create_summary"),
            json={"url": "https://foo.bar"},
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 201

        summary = authorized_response.json()
        payload = {
            "username": "not_owner",
            "email": "not_owner@mail.com",
            "full_name": "Not Owner",
            "password": "secret",
        }
        not_owner_response = await client.post(url=app.url_path_for("create_user"), json=payload)
        assert not_owner_response.status_code == 201

        authorization = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": payload["username"], "password": payload["password"]},
        )
        tokens = authorization.json()
        token_for_not_owner = tokens["access_token"]
        not_owner_response = await client.delete(
            url=app.url_path_for("delete_summary", id=summary["id"]),
            headers={"Authorization": f"Bearer {token_for_not_owner}"},
        )
        assert not_owner_response.status_code == 403
        assert not_owner_response.json()["detail"] == "Insufficient rights to delete this summary"


@pytest.mark.asyncio
async def test_delete_summary_incorrect_id(test_client_with_db):
    async with test_client_with_db as client:
        await client.post(url=app.url_path_for("create_user"), json=TEST_USER)
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
        )
        tokens = response.json()
        issued_test_token = tokens["access_token"]

        unauthorized_response = await client.delete(url=app.url_path_for("delete_summary", id=TEST_ID))
        assert unauthorized_response.status_code == 401

        authorized_response = await client.delete(
            url=app.url_path_for("delete_summary", id=TEST_ID),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )

        authorized_response = await client.delete(
            url=app.url_path_for("delete_summary", id=TEST_ID),
            headers={"Authorization": f"Bearer {issued_test_token}"},
        )
        assert authorized_response.status_code == 404
        assert authorized_response.json()["detail"] == "Summary not found"
