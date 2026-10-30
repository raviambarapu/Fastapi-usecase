import uuid


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_register(client):
    email = unique_email()

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Test User"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Test User"


def test_login(client):
    email = unique_email()

    # First register
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Login Test User"
        }
    )

    assert register_response.status_code == 201

    # Then login
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login(client):
    email = unique_email()

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Invalid Login Test"
        }
    )

    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code in [400, 401]


def test_duplicate_registration(client):
    email = unique_email()

    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Duplicate Test"
    }

    first_response = client.post(
        "/auth/register",
        json=payload
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json=payload
    )

    assert second_response.status_code == 409


def test_me(client):
    email = unique_email()

    # Register
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Me Test User"
        }
    )

    # Login
    login_response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": "Password123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Call /me
    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email