import json
import shutil

from .conftest import app


def test_generate_summary(test_app_with_db):
    try:
        # Prepare a test state in case the nltk_data folder has already been created.
        shutil.rmtree("/home/app/nltk_data")
    except FileNotFoundError:
        pass
    response = test_app_with_db.post(
        app.url_path_for("create_summary"),
        data=json.dumps({"url": "https://lipsum.com/"}),
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.get(app.url_path_for("read_summary", id=summary_id))
    assert "Lorem Ipsum" in response.json()["summary"]
