import asyncio
import logging
import redis.asyncio as aioredis
from fakeredis import FakeAsyncRedis
fake_redis = FakeAsyncRedis(decode_responses=True)
aioredis.from_url = lambda *args, **kwargs: fake_redis

from fastapi.testclient import TestClient
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_security_flow")

def test_security_flow():
    import uuid
    with TestClient(app) as client:
        email = f"securetest_{uuid.uuid4().hex[:8]}@example.com"
        password = "strongpassword123"

        # 1. Register a user
        logger.info("Registering user...")
        response = client.post("/api/v1/users/register", json={
            "email": email,
            "password": password
        })
        if response.status_code == 201:
            logger.info("Registration successful")
        else:
            logger.error(f"Registration failed: {response.text}")
            return
            
        # 2. Login before verify - should fail
        logger.info("Attempting login before verification...")
        response = client.post("/api/v1/auth/login/access-token", data={
            "username": email,
            "password": password
        })
        if response.status_code == 403 and "verified" in response.text:
            logger.info("Login blocked correctly (Unverified)")
        else:
            logger.error(f"Login should have been blocked, got: {response.status_code} - {response.text}")
            return
            
        # Extract verification token directly from redis for testing
        from app.redis_client import get_redis
        
        async def get_token(prefix):
            r = await get_redis()
            keys = await r.keys(f"{prefix}:*")
            return keys[0].split(":")[1] if keys else None
            
        verify_token = asyncio.run(get_token("email_verify"))
        
        # 3. Verify email
        logger.info(f"Verifying email with token: {verify_token}")
        response = client.post("/api/v1/users/verify-email", json={"token": verify_token})
        if response.status_code == 200:
            logger.info("Email verified")
        else:
            logger.error(f"Verification failed: {response.text}")
            return
            
        # 4. Login after verify
        logger.info("Logging in after verification...")
        response = client.post("/api/v1/auth/login/access-token", data={
            "username": email,
            "password": password
        })
        if response.status_code == 200:
            logger.info("Login successful")
            tokens = response.json()
            access_token = tokens["access_token"]
        else:
            logger.error(f"Login failed: {response.text}")
            return
            
        # 5. Access protected route
        logger.info("Accessing /me...")
        response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code == 200:
            logger.info("Protected route accessed")
        else:
            logger.error(f"Protected route failed: {response.text}")
            
        # 6. Password reset request
        logger.info("Requesting password reset...")
        response = client.post("/api/v1/auth/password-reset/request", json={"email": email})
        if response.status_code == 200:
            logger.info("Password reset requested")
        else:
            logger.error(f"Password reset request failed: {response.text}")
            return
            
        reset_token = asyncio.run(get_token("password_reset"))
        
        # 7. Confirm password reset
        logger.info("Confirming password reset...")
        new_password = "newstrongpassword456"
        response = client.post("/api/v1/auth/password-reset/confirm", json={
            "token": reset_token,
            "new_password": new_password
        })
        if response.status_code == 200:
            logger.info("Password reset confirmed")
        else:
            logger.error(f"Password reset confirm failed: {response.text}")
            return
            
        # 8. Try to access with old token (should be revoked)
        logger.info("Testing global session revocation...")
        response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code == 401:
            logger.info("Old session globally revoked successfully")
        else:
            logger.error(f"Global revocation failed, got: {response.status_code}")
            
        # 9. Test Brute force
        logger.info("Testing Brute Force Protection...")
        for i in range(5):
            response = client.post("/api/v1/auth/login/access-token", data={"username": email, "password": "wrong"})
        
        # The 6th should be 429
        response = client.post("/api/v1/auth/login/access-token", data={"username": email, "password": "wrong"})
        if response.status_code == 429:
            logger.info("Brute force protection triggered correctly")
        else:
            logger.error(f"Brute force failed to trigger: {response.status_code}")

if __name__ == "__main__":
    test_security_flow()
