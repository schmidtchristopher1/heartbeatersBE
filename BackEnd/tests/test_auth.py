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


# Tests for the /register/person endpoint
def test_register_person(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    assert response.status_code == 201
    assert response.json == {"message": "Person registered successfully"}

    # Attempt to register the same email again
    response = client.post(
        "/auth/register",
        json={
            "first_name": "test2",
            "last_name": "user2",
            "email": "testuser@example.com",
            "password": "testpassword2",
            "gender": "female",
        },
    )
    assert response.status_code == 400
    assert response.json == {"error": "Email already registered"}


def test_register_person_missing_fields(client):
    response = client.post(
        "/auth/register", json={"username": "testuser", "email": "testuser@example.com"}
    )
    assert response.status_code == 400
    assert response.json == {"error": "First name is required"}


def test_register_person_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "invalid-email",
            "password": "testpassword",
            "gender": "male",
        },
    )
    assert response.status_code == 400
    assert response.json == {"error": "Invalid email address"}


def test_register_person_duplicate_email(client):
    client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    response = client.post(
        "/auth/register",
        json={
            "first_name": "test2",
            "last_name": "user2",
            "email": "testuser@example.com",
            "password": "testpassword2",
            "gender": "female",
        },
    )
    assert response.status_code == 400
    assert response.json == {"error": "Email already registered"}


# Tests for the /login endpoint
def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json


def test_login_missing_fields(client):
    response = client.post("/auth/login", json={"email": "testuser@example.com"})
    assert response.status_code == 400
    assert response.json == {"error": "Password is required"}


def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "testpassword"},
    )
    assert response.status_code == 401
    assert response.json == {"error": "Unknown email address"}


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json == {"error": "Invalid password"}


def test_login_failure(client):
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json == {"error": "Unknown email address"}

    client.post(
        "/auth/register",
        json={
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@example.com",
            "password": "testpassword",
            "gender": "male",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json == {"error": "Invalid password"}
