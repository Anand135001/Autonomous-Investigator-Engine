from fastapi.testclient import TestClient

from investigator.api.app import app


client = TestClient(app)


def test_health() -> None:

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_unknown_case() -> None:

    response = client.post(
        "/investigations",
        json={
            "case_id": "does_not_exist"
        },
    )

    assert response.status_code == 404