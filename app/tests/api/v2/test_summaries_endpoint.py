import pytest

from app.background.tasks import celery_generate_summary
from app.config import get_settings
from app.main import app

TEST_UUID = "0d1cce70-f99c-42bb-a96c-ef8e9b540e67"

settings = get_settings()


def test_create_summary(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    assert authorized_response.json()["url"] == "https://foo.bar"


def test_create_summaries_invalid_json(test_client_with_db, create_test_user, issued_test_token):
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 422
    assert authorized_response.json()["detail"][0] == {
        "loc": ["body", "url"],
        "msg": "field required",
        "type": "value_error.missing",
    }
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "invalid://url"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 422
    assert authorized_response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_read_summary(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    response = test_client_with_db.get(url=app.url_path_for("read_summary", id=summary["id"]))
    assert response.status_code == 200
    assert response.json() == {
        "id": summary["id"],
        "url": "https://foo.bar",
        "summary": "",
        "user_id": summary["user_id"],
    }


def test_read_summary_incorrect_id(test_client_with_db):
    response = test_client_with_db.get(url=app.url_path_for("read_summary", id=TEST_UUID))
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    response = test_client_with_db.get(url=app.url_path_for("read_all_summaries"))
    assert response.status_code == 200
    assert len(list(filter(lambda s: s["id"] == summary["id"], response.json()))) == 1


def test_update_summary(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    unauthorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=summary["id"]),
        json={"url": "https://updated.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=summary["id"]),
        json={"url": "https://updated.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 200
    assert authorized_response.json() == {
        "id": summary["id"],
        "url": "https://updated.bar",
        "summary": "",
        "user_id": summary["user_id"],
    }


@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            TEST_UUID,
            {"url": "https://foo.bar"},
            404,
            "Summary not found",
        ],
        [
            TEST_UUID,
            {},
            422,
            [
                {
                    "loc": ["body", "url"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        ],
        [
            TEST_UUID,
            {"url": "foo.bar"},
            422,
            [
                {
                    "loc": ["body", "url"],
                    "msg": "invalid or missing URL scheme",
                    "type": "value_error.url.scheme",
                },
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_client_with_db, create_test_user, issued_test_token, summary_id, payload, status_code, detail
):
    unauthorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=summary_id),
        json=payload,
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=summary_id),
        json=payload,
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == status_code
    assert authorized_response.json()["detail"] == detail


def test_update_summary_invalid_url(test_client_with_db, create_test_user, issued_test_token):
    unauthorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=TEST_UUID),
        json={"url": "invalid://url"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.put(
        url=app.url_path_for("update_summary", id=TEST_UUID),
        json={"url": "invalid://url"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 422
    assert authorized_response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_update_summary_without_rights(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    payload = {"username": "not_owner", "email": "not_owner@mail.com", "full_name": "Not Owner", "password": "secret"}
    not_owner_response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert not_owner_response.status_code == 201
    authorization = test_client_with_db.post(
        url=app.url_path_for("issue_access_token"),
        data={"username": payload["username"], "password": payload["password"]},
    )
    tokens = authorization.json()
    token_for_not_owner = tokens["access_token"]
    not_owner_response = test_client_with_db.put(
        url=app.url_path_for("delete_summary", id=summary["id"]),
        json={"url": "https://updated.bar"},
        headers={"Authorization": f"Bearer {token_for_not_owner}"},
    )
    assert not_owner_response.status_code == 403
    assert not_owner_response.json()["detail"] == "Insufficient rights to update this summary"


def test_delete_summary(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    unauthorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
    )
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    unauthorized_response = test_client_with_db.delete(url=app.url_path_for("delete_summary", id=summary["id"]))
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.delete(
        url=app.url_path_for("delete_summary", id=summary["id"]),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 200
    assert authorized_response.json() == {
        "id": summary["id"],
        "url": "https://foo.bar",
        "summary": "",
        "user_id": summary["user_id"],
    }


def test_delete_summary_without_rights(test_client_with_db, create_test_user, issued_test_token, monkeypatch):
    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    authorized_response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://foo.bar"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 201
    summary = authorized_response.json()
    payload = {"username": "not_owner", "email": "not_owner@mail.com", "full_name": "Not Owner", "password": "secret"}
    not_owner_response = test_client_with_db.post(url=app.url_path_for("create_user"), json=payload)
    assert not_owner_response.status_code == 201
    authorization = test_client_with_db.post(
        url=app.url_path_for("issue_access_token"),
        data={"username": payload["username"], "password": payload["password"]},
    )
    tokens = authorization.json()
    token_for_not_owner = tokens["access_token"]
    not_owner_response = test_client_with_db.delete(
        url=app.url_path_for("delete_summary", id=summary["id"]),
        headers={"Authorization": f"Bearer {token_for_not_owner}"},
    )
    assert not_owner_response.status_code == 403
    assert not_owner_response.json()["detail"] == "Insufficient rights to delete this summary"


def test_delete_summary_incorrect_id(test_client_with_db, create_test_user, issued_test_token):
    unauthorized_response = test_client_with_db.delete(url=app.url_path_for("delete_summary", id=TEST_UUID))
    assert unauthorized_response.status_code == 401
    authorized_response = test_client_with_db.delete(
        url=app.url_path_for("delete_summary", id=TEST_UUID),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    authorized_response = test_client_with_db.delete(
        url=app.url_path_for("delete_summary", id=TEST_UUID),
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    assert authorized_response.status_code == 404
    assert authorized_response.json()["detail"] == "Summary not found"
