import json
from datetime import datetime

import pytest

from app.background.tasks import celery_generate_summary
from app.crud import crud_summary

from .conftest import app


def test_create_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://foo.bar"}
    test_response_payload = {"id": 1, "url": "https://foo.bar"}

    async def mock_post(payload):
        return 1

    monkeypatch.setattr(crud_summary, "post", mock_post)

    def mock_delay(summary_id, url):
        return None

    monkeypatch.setattr(celery_generate_summary, "delay", mock_delay)
    response = test_app.post(
        app.url_path_for("create_summary"),
        data=json.dumps(test_request_payload),
    )
    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_summaries_invalid_json(test_app):
    response = test_app.post(
        app.url_path_for("create_summary"),
        data=json.dumps({}),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
    response = test_app.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "invalid://url"}),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_read_summary(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "summary",
        "created_at": datetime.utcnow().isoformat(),
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud_summary, "get", mock_get)
    response = test_app.get(app.url_path_for("read_summary", id=1))
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_summary_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud_summary, "get", mock_get)
    response = test_app.get(app.url_path_for("read_summary", id=999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(test_app, monkeypatch):
    test_data = [
        {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": 2,
            "url": "https://testdrivenn.io",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        },
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud_summary, "get_all", mock_get_all)
    response = test_app.get(app.url_path_for("read_all_summaries"))
    assert response.status_code == 200
    assert response.json() == test_data


def test_update_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://foo.bar", "summary": "updated"}
    test_response_payload = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "summary",
        "created_at": datetime.utcnow().isoformat(),
    }

    async def mock_put(id, payload):
        return test_response_payload

    monkeypatch.setattr(crud_summary, "put", mock_put)
    response = test_app.put(
        app.url_path_for("update_summary", id=1),
        data=json.dumps(test_request_payload),
    )
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            999,
            {"url": "https://foo.bar", "summary": "updated!"},
            404,
            "Summary not found",
        ],
        [
            0,
            {"url": "https://foo.bar", "summary": "updated!"},
            422,
            [
                {
                    "loc": ["path", "id"],
                    "msg": "ensure this value is greater than 0",
                    "type": "value_error.number.not_gt",
                    "ctx": {"limit_value": 0},
                }
            ],
        ],
        [
            1,
            {},
            422,
            [
                {
                    "loc": ["body", "url"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        ],
        [
            1,
            {"url": "https://foo.bar"},
            422,
            [
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
        ],
    ],
)
def test_update_summary_invalid(test_app, monkeypatch, summary_id, payload, status_code, detail):
    async def mock_put(id, payload):
        return None

    monkeypatch.setattr(crud_summary, "put", mock_put)
    response = test_app.put(app.url_path_for("update_summary", id=summary_id), data=json.dumps(payload))
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    response = test_app.put(
        app.url_path_for("update_summary", id=1),
        data=json.dumps({"url": "invalid://url", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_delete_summary(test_app, monkeypatch):
    async def mock_get(id):
        return {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        }

    monkeypatch.setattr(crud_summary, "get", mock_get)

    async def mock_delete(id):
        return id

    monkeypatch.setattr(crud_summary, "delete", mock_delete)
    response = test_app.delete(app.url_path_for("delete_summary", id=1))
    assert response.status_code == 200
    assert response.json() == {"id": 1, "url": "https://foo.bar"}


def test_delete_summary_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud_summary, "get", mock_get)
    response = test_app.delete(app.url_path_for("delete_summary", id=999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
