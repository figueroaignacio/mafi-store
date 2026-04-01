from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)


@router.get("/google")
def google_login():
    params = (
        f"client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.API_URL}/auth/google/callback"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"}


@router.get("/google/callback")
async def google_callback(
    code: str,
    service: AuthService = Depends(get_auth_service),
):
    token = await service.get_google_user(code)
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/github")
def github_login():
    params = (
        f"client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.API_URL}/auth/github/callback"
        f"&scope=user:email"
    )
    return {"url": f"https://github.com/login/oauth/authorize?{params}"}


@router.get("/github/callback")
async def github_callback(
    code: str,
    service: AuthService = Depends(get_auth_service),
):
    token = await service.get_github_user(code)
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout exitoso"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
