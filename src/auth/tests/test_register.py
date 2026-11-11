import pytest

REGISTER_URL = "/api/v1/auth/register"

@pytest.mark.asyncio
async def test_register_user(async_client):
    payload = {
        "email": "test_unique@test.com",
        "password": "test_123123123"
    }

    response = await async_client.post(
        REGISTER_URL,
        json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "uuid" in data
    assert "role" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client):
    payload = {
        "email": "duplicate_test@test.com",
        "password": "test_123123123"
    }
    res1 = await async_client.post(REGISTER_URL, json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post(REGISTER_URL, json=payload)
    assert res2.status_code == 409
    assert res2.json()["detail"] == "Email already registered."


@pytest.mark.parametrize(
    "extra_fields",
    [
        {"role": "admin"},
        {"is_active": False},
        {"uuid": 999},
    ],
)

async def test_register_ignores_privileged_fields(async_client, extra_fields):
    payload = {
        "email": "hacker@test.com",
        "password": "test_123123123",
        **extra_fields,
    }

    response = await async_client.post(REGISTER_URL, json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert data["uuid"] != 999