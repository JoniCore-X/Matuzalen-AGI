from typing import Any

from app.integrations.supabase_client import SupabaseClient
from fastapi import HTTPException, status

supabase = SupabaseClient()


def register_user(email: str, password: str, full_name: str | None = None) -> dict[str, Any]:
    try:
        response = supabase.client.auth.sign_up(
            {
                'email': email,
                'password': password,
                'options': {'data': {'full_name': full_name or ''}},
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to register this account',
        ) from exc

    if response.session is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail='Check your email to confirm the account before signing in',
        )
    return _session_to_user(response.session)


def authenticate_user(email: str, password: str) -> dict[str, Any]:
    try:
        response = supabase.client.auth.sign_in_with_password(
            {'email': email, 'password': password}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        ) from exc
    return _session_to_user(response.session)


def request_password_reset(email: str, redirect_to: str) -> None:
    try:
        supabase.client.auth.reset_password_for_email(
            email,
            {'redirect_to': redirect_to},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Unable to send the password reset email',
        ) from exc


def get_user_from_token(token: str) -> dict[str, Any] | None:
    try:
        user = supabase.get_user(token)
    except Exception:
        return None

    if user is None:
        return None

    metadata = user.user_metadata or {}
    return {
        'id': str(user.id),
        'email': user.email,
        'full_name': metadata.get('full_name'),
    }


def build_token_for_user(user: dict[str, Any]) -> str:
    return user['access_token']


def _session_to_user(session: Any) -> dict[str, Any]:
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unable to create an authenticated session',
        )
    return {'access_token': session.access_token}
