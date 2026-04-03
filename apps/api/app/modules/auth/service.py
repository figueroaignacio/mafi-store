import httpx

from app.core.config import settings
from app.core.security import create_access_token
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_or_create_user(
        self, email: str, name: str, avatar_url: str | None
    ) -> str:
        user = await self.repository.get_by_email(email)
        if not user:
            user = await self.repository.create(
                UserCreate(email=email, name=name, avatar_url=avatar_url)
            )
        return create_access_token(str(user.id))

    async def get_google_user(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": "http://localhost:8000/auth/google/callback",
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_res.json()
            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_data = user_res.json()

        return await self.get_or_create_user(
            email=user_data["email"],
            name=user_data["name"],
            avatar_url=user_data.get("picture"),
        )

    async def get_github_user(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "code": code,
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                },
            )
            token_data = token_res.json()
            user_res = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_data = user_res.json()

            email = user_data.get("email")
            if not email:
                email_res = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"},
                )
                emails = email_res.json()
                email = next(e["email"] for e in emails if e["primary"])

        return await self.get_or_create_user(
            email=email,
            name=user_data["name"] or user_data["login"],
            avatar_url=user_data.get("avatar_url"),
        )
