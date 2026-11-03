import pytest
from datetime import timedelta

REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"


@pytest.mark.asyncio
async def test_refresh_tokens(async_client, auth_tokens):
    refresh_token = auth_tokens["refresh_token"]

    get_new_refresh_token = await async_client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert get_new_refresh_token.status_code == 200

    new_tokens = get_new_refresh_token.json()

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_logout_revokes_access_token(authenticated_client, auth_tokens):
    access_token = authenticated_client.headers["Authorization"].split(" ")[1]
    refresh_token = auth_tokens["refresh_token"]

    me = await authenticated_client.get(ME_URL)
    assert me.status_code == 200

    logout = await authenticated_client.post(LOGOUT_URL, json={"refresh_token": refresh_token})
    assert logout.status_code == 200

    unauth_me = await authenticated_client.get(ME_URL)
    assert unauth_me.status_code == 401
    assert unauth_me.json()["detail"] == "Token has been revoked (logged out)."


@pytest.mark.asyncio
async def test_refresh_token_reuse(async_client, auth_tokens):
    refresh_token = auth_tokens["refresh_token"]

    first_refresh = await async_client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert first_refresh.status_code == 200

    second_refresh = await async_client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert second_refresh.status_code == 401
    assert "Token reuse detected" in second_refresh.json()["detail"]


async def test_logout_without_refresh_token(authenticated_client):
    logout = await authenticated_client.post(LOGOUT_URL)
    assert logout.status_code == 200

    me = await authenticated_client.get(ME_URL)
    assert me.status_code == 401