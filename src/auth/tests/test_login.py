import pytest

@pytest.mark.asyncio
async def test_login_user(async_client):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login123@text.com","password": "123123123"}
    )

    response = await async_client.post(
        "/api/v1/auth/login",
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
        "/api/v1/auth/login",
        data={"username": "login123@text.com", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."