import json

import pytest

from app.api.v2.endpoints import summaries

from .conftest import app


def test_create_summary(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://foo.bar"}),
    )
    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"


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


def test_read_summary(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.get(app.url_path_for("read_summary", id=summary_id))
    assert response.status_code == 200
    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"] == ""
    assert response_dict["created_at"]


def test_read_summary_incorrect_id(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.get(app.url_path_for("read_summary", id=999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
    response = test_app_with_db.get(app.url_path_for("read_summary", id=0))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_read_all_summaries(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.get(app.url_path_for("read_all_summaries"))
    assert response.status_code == 200
    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_update_summary(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.put(
        app.url_path_for("update_summary", id=summary_id),
        data=json.dumps({"url": "https://foo.bar", "summary": "updated!"}),
    )
    assert response.status_code == 200
    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"] == "updated!"
    assert response_dict["created_at"]


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
def test_update_summary_invalid(test_app_with_db, monkeypatch, summary_id, payload, status_code, detail):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.put(
        app.url_path_for("update_summary", id=summary_id),
        data=json.dumps(payload),
    )
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    response = test_app.put(
        app.url_path_for("update_summary", id=1),
        data=json.dumps({"url": "invalid://url", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_delete_summary(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.delete(app.url_path_for("delete_summary", id=summary_id))
    assert response.status_code == 200
    assert response.json() == {"id": summary_id, "url": "https://foo.bar"}


def test_delete_summary_incorrect_id(test_app_with_db, monkeypatch):
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)
    response = test_app_with_db.delete(app.url_path_for("delete_summary", id=999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
    response = test_app_with_db.delete(app.url_path_for("delete_summary", id=0))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }
