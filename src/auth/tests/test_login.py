import pytest

LOGIN_URL = "/api/v1/auth/login"


@pytest.mark.asyncio
async def test_login_user(async_client):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login123@text.com","password": "123123123"}
    )

    response = await async_client.post(
        LOGIN_URL,
        data={"username": "login123@text.com","password": "123123123"}
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login123@text.com", "password": "123123123"}
    )
    response = await async_client.post(
        LOGIN_URL,
        data={"username": "login123@text.com", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


async def test_login_rate_limit(async_client, registered_user):
    wrong = {"username": registered_user["email"], "password": "wrong_password"}
    for _ in range(10):
        response = await async_client.post(LOGIN_URL, data=wrong)
        assert response.status_code == 401

    blocked = await async_client.post(LOGIN_URL, data=wrong)
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


async def test_rate_limit_blocks_even_correct_password(async_client, registered_user):
    wrong = {"username": registered_user["email"], "password": "wrong_password"}
    for _ in range(10):
        await async_client.post(LOGIN_URL, data=wrong)

    correct = {"username": registered_user["email"], "password": registered_user["password"]}
    response = await async_client.post(LOGIN_URL, data=correct)

    assert response.status_code == 429