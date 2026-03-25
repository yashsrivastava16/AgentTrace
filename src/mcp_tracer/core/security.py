"""
JWT authentication for AgentTrace.
Handles token creation and verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from fastmcp.exceptions import ToolError

from mcp_tracer.core.config import settings


def create_agent_token(subject: str) -> str:
    """
    General purpose agent token — no session scope.
    Used for create_session and other session-agnostic calls.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": "agent",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_session_token(subject: str, session_id: str) -> str:
    """
    Session-scoped token — locked to one session_id.
    Use this after create_session returns a session_id.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": "session",
        "session_id": session_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise ToolError(f"Unauthorized: {str(e)}")
    """
    Verify a JWT token and return its payload.
    Raises ToolError if token is invalid or expired.

    Args:
        token: Raw JWT string (without 'Bearer ' prefix)

    Returns:
        Decoded token payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise ToolError(f"Unauthorized: {str(e)}")