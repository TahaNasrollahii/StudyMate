import asyncio
import logging
from fastapi.testclient import TestClient
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_auth_flow")

def test_auth():
    with TestClient(app) as client:
        # 1. Register a user
        logger.info("Registering user...")
        response = client.post("/api/v1/users/register", json={
            "email": "test@example.com",
            "password": "strongpassword123"
        })
        if response.status_code == 201:
            logger.info("Registration successful")
        else:
            logger.error(f"Registration failed: {response.text}")
            return

        # 2. Login
        logger.info("Logging in...")
        response = client.post("/api/v1/auth/login/access-token", data={
            "username": "test@example.com",
            "password": "strongpassword123"
        })
        if response.status_code == 200:
            logger.info("Login successful")
            tokens = response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
        else:
            logger.error(f"Login failed: {response.text}")
            return

        # 3. Access protected route (/api/v1/users/me)
        logger.info("Accessing /me...")
        response = client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {access_token}"
        })
        if response.status_code == 200:
            logger.info(f"/me returned: {response.json()['email']}")
        else:
            logger.error(f"Access /me failed: {response.text}")
            return

        # 4. Refresh token
        logger.info("Refreshing token...")
        response = client.post(f"/api/v1/auth/refresh?refresh_token={refresh_token}")
        if response.status_code == 200:
            logger.info("Token refresh successful")
            new_tokens = response.json()
            new_access = new_tokens["access_token"]
            new_refresh = new_tokens["refresh_token"]
        else:
            logger.error(f"Refresh failed: {response.text}")
            return

        # 5. Logout
        logger.info("Logging out...")
        response = client.post(f"/api/v1/auth/logout?refresh_token={new_refresh}", headers={
            "Authorization": f"Bearer {new_access}"
        })
        if response.status_code == 200:
            logger.info("Logout successful")
        else:
            logger.error(f"Logout failed: {response.text}")
            return

        # 6. Verify refresh token is blocked
        logger.info("Verifying refresh token is revoked...")
        response = client.post(f"/api/v1/auth/refresh?refresh_token={new_refresh}")
        if response.status_code == 401:
            logger.info("Revocation verified")
        else:
            logger.error(f"Revocation failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_auth()
