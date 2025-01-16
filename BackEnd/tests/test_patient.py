import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            from app.init_db import InitDB

            InitDB.flush_db()
            InitDB.seed_db()
        yield client


def test_get_patients(client):
    # Register first test user
    register_response = client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    assert register_response.status_code == 201

    # Register second test user
    register_response1 = client.post(
        "/auth/register",
        json={
            "first_name": "test1",
            "last_name": "user1",
            "email": "test1user1@example.com",
            "password": "testpassword1",
            "gender": "female",
        },
    )
    assert register_response1.status_code == 201

    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "testpassword",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json["access_token"]

    # Get patients with authentication
    response = client.get("/patients", headers={"Authorization": f"Bearer {token}"})

    # Verify response structure and data
    assert response.status_code == 200
    assert response.json["total"] == 2  # Expected 2 patients
    assert len(response.json["data"]) == 2  # Verify data array length

    # Verify first patient data
    assert response.json["data"][0]["email"] == "testuser@example.com"
    assert response.json["data"][0]["first_name"] == "test"
    assert response.json["data"][0]["last_name"] == "user"
    assert response.json["data"][0]["gender"] == "male"

    # Verify second patient data
    assert response.json["data"][1]["email"] == "test1user1@example.com"
    assert response.json["data"][1]["first_name"] == "test1"
    assert response.json["data"][1]["last_name"] == "user1"
    assert response.json["data"][1]["gender"] == "female"
