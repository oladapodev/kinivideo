from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_from_tiktok_url():
    response = client.post(
        "/jobs",
        data={
            "source_url": "https://www.tiktok.com/@creator/video/1234567890",
            "recipe_ids": '["hot-take","qa"]',
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["job"]["source_type"] == "tiktok_replay"
    assert payload["job"]["status"] == "ready"
    assert len(payload["transcript"]) > 0
    assert len(payload["clips"]) > 0


def test_recipe_rerun_and_export():
    create_response = client.post(
        "/jobs",
        data={
            "source_url": "https://www.tiktok.com/@creator/video/999999999",
            "recipe_ids": '["hot-take","explainer-tip"]',
        },
    )
    job = create_response.json()
    job_id = job["job"]["id"]
    rerun_response = client.post(
        f"/jobs/{job_id}/recipes/run",
        json={"recipe_ids": ["news-recap"]},
    )
    assert rerun_response.status_code == 200
    rerun_job = rerun_response.json()
    assert rerun_job["job"]["selected_recipe_ids"] == ["news-recap"]
    clip_id = rerun_job["clips"][0]["id"]

    approve_response = client.post(f"/clips/{clip_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    export_response = client.post(f"/clips/{clip_id}/export")
    assert export_response.status_code == 200
    exported_clip = export_response.json()
    assert exported_clip["status"] == "exported"
    assert exported_clip["export_package"]["file_path"].endswith(".mp4")
