# tests/test_users.py
"""
Unit tests for user service (app/services/users.py).
Tests business logic layer independently.
"""

import pytest
from app.services.users import (
    create_user,
    authenticate_user,
    get_user_by_identifier,
    IdentifierAlreadyUsedError,
)


class TestCreateUser:
    """Tests for create_user service function."""

    def test_create_user_success(self, db_session):
        """create_user should create a user row in the database."""
        user = create_user(
            db=db_session,
            identifier="newuser@example.com",
            password="password123",
        )

        assert user is not None
        assert user.id is not None
        assert user.identifier == "newuser@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "password123"  # Should be hashed

    def test_create_user_duplicate_raises_error(self, db_session):
        """create_user should raise IdentifierAlreadyUsedError for duplicate identifier."""
        # Create first user
        create_user(
            db=db_session,
            identifier="duplicate@example.com",
            password="password123",
        )

        # Attempt to create duplicate
        with pytest.raises(IdentifierAlreadyUsedError):
            create_user(
                db=db_session,
                identifier="duplicate@example.com",
                password="different_password",
            )


class TestAuthenticateUser:
    """Tests for authenticate_user service function."""

    def test_authenticate_user_success(self, db_session):
        """authenticate_user should return user when password is correct."""
        # Create user first
        create_user(
            db=db_session,
            identifier="auth_test@example.com",
            password="correctpassword",
        )

        # Authenticate with correct password
        user = authenticate_user(
            db=db_session,
            identifier="auth_test@example.com",
            password="correctpassword",
        )

        assert user is not None
        assert user.identifier == "auth_test@example.com"

    def test_authenticate_user_wrong_password(self, db_session):
        """authenticate_user should return None when password is wrong."""
        # Create user first
        create_user(
            db=db_session,
            identifier="auth_fail@example.com",
            password="correctpassword",
        )

        # Authenticate with wrong password
        user = authenticate_user(
            db=db_session,
            identifier="auth_fail@example.com",
            password="wrongpassword",
        )

        assert user is None

    def test_authenticate_user_nonexistent(self, db_session):
        """authenticate_user should return None for non-existent user."""
        user = authenticate_user(
            db=db_session,
            identifier="nonexistent@example.com",
            password="anypassword",
        )

        assert user is None





