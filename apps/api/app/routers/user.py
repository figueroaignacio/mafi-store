import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID, service: UserService = Depends(get_user_service)
):
    return await service.get_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create(data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID, service: UserService = Depends(get_user_service)
):
    await service.delete(user_id)
