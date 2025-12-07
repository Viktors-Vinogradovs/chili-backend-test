# tests/test_auth_api.py
"""
API tests for auth endpoints (app/api/v1/auth.py).
Tests full request/response cycle through FastAPI.
"""

import pytest


class TestRegister:
    """Tests for POST /auth/register endpoint."""

    def test_register_success(self, client):
        """Register should return 201 with user and token."""
        response = client.post(
            "/auth/register",
            json={
                "identifier": "newuser@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "success"
        assert "user" in data["data"]
        assert "token" in data["data"]
        assert data["data"]["user"]["identifier"] == "newuser@example.com"
        assert "access_token" in data["data"]["token"]
        assert data["data"]["token"]["token_type"] == "bearer"

    def test_register_duplicate(self, client):
        """Register with existing identifier should return 400 fail."""
        # Register first user
        client.post(
            "/auth/register",
            json={
                "identifier": "duplicate@example.com",
                "password": "password123",
            },
        )

        # Try to register with same identifier
        response = client.post(
            "/auth/register",
            json={
                "identifier": "duplicate@example.com",
                "password": "different_password",
            },
        )

        assert response.status_code == 400
        data = response.json()
        
        assert data["status"] == "fail"
        assert "identifier" in data["data"]


class TestLogin:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, client, registered_user):
        """Login with correct credentials should return 200 with token."""
        response = client.post(
            "/auth/login",
            json=registered_user["credentials"],
        )

        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "user" in data["data"]
        assert "token" in data["data"]
        assert "access_token" in data["data"]["token"]

    def test_login_wrong_password(self, client, registered_user):
        """Login with wrong password should return 401 fail."""
        response = client.post(
            "/auth/login",
            json={
                "identifier": registered_user["credentials"]["identifier"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        
        assert data["status"] == "fail"
        assert "credentials" in data["data"]

    def test_login_nonexistent_user(self, client):
        """Login with non-existent user should return 401 fail."""
        response = client.post(
            "/auth/login",
            json={
                "identifier": "nonexistent@example.com",
                "password": "anypassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        
        assert data["status"] == "fail"


class TestAvatar:
    """Tests for POST /auth/avatar endpoint."""

    def test_avatar_requires_auth(self, client):
        """Avatar upload without token should return 401."""
        response = client.post("/auth/avatar")

        # No credentials → 401 Unauthorized
        assert response.status_code == 401


class TestDeleteUser:
    """Tests for DELETE /auth/me endpoint."""

    def test_delete_user_success(self, client, registered_user):
        """Delete user should return 200 and user should be gone."""
        token = registered_user["token"]
        
        # Delete user
        response = client.delete(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "message" in data["data"]

        # Verify user can no longer login
        login_response = client.post(
            "/auth/login",
            json=registered_user["credentials"],
        )
        assert login_response.status_code == 401

    def test_delete_requires_auth(self, client):
        """Delete without token should return 401."""
        response = client.delete("/auth/me")

        assert response.status_code == 401

