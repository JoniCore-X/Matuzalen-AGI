from app.dependencies import get_current_user
from app.modules.auth.schemas import (PasswordResetRequest, TokenResponse,
                                      UserLogin, UserOut, UserRegister)
from app.modules.auth.service import (authenticate_user, build_token_for_user,
                                      register_user, request_password_reset)
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user_route(payload: UserRegister):
    user = register_user(payload.email, payload.password, payload.full_name)
    token = build_token_for_user(user)
    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/login', response_model=TokenResponse)
def login_user_route(payload: UserLogin):
    user = authenticate_user(payload.email, payload.password)
    token = build_token_for_user(user)
    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/password-reset', status_code=status.HTTP_202_ACCEPTED)
def password_reset_route(payload: PasswordResetRequest):
    request_password_reset(payload.email, payload.redirect_to)
    return {'message': 'If the account exists, a reset email has been sent'}


@router.get('/me', response_model=UserOut)
def get_current_user_route(current_user=Depends(get_current_user)):
    return {
        'id': current_user['id'],
        'email': current_user['email'],
        'full_name': current_user['full_name'],
    }
