import uuid

from fastapi import HTTPException

from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserResponse


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> UserResponse | None:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def create(self, data: UserCreate) -> UserResponse:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        user = await self.repository.create(data)
        return UserResponse.model_validate(user)

    async def delete(self, user_id: uuid.UUID) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        await self.repository.delete(user)
