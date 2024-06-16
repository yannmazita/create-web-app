from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.users.dependencies import get_own_user
from app.users.models import (
    User,
)
from app.users.repository import UserRepository
from app.users.schemas import (
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserRolesUpdate,
    UserUsernameUpdate,
)
from app.users.services import UserAdminService, UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserRead)
async def create_user(
    user: UserCreate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: AsyncSession = Depends(get_session),
):
    repository = UserRepository(session)
    service = UserService(repository)

    new_user = await service.create_user(user)
    return new_user


@router.get("/id/{id}", response_model=UserRead)
async def get_user_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    service = UserService(repository)
    user = await service.get_user(id)
    return user


@router.get("/all", response_model=tuple[list[UserRead], int])
async def get_all_users(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = 100,
):
    repository = UserRepository(session)
    service = UserService(repository)
    users, total_count = await service.get_users(offset, limit)
    return users, total_count


@router.put("/id/{id}", response_model=UserRead)
async def update_user_by_id(
    id: UUID,
    user: User,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    service = UserService(repository)
    updated_user = await service.update_user(id, user)
    return updated_user


@router.delete("/id/{id}", response_model=UserRead)
async def delete_user_by_id(
    id: UUID,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    service = UserService(repository)
    user = await service.delete_user(id)
    return user


@router.patch("/id/{id}/username", response_model=UserRead)
async def update_user_username_by_id(
    id: UUID,
    username_data: UserUsernameUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    admin_service = UserAdminService(repository)
    updated_user = await admin_service.update_user_username(id, username_data)
    return updated_user


@router.patch("/id/{id}/roles", response_model=UserRead)
async def update_user_roles_by_id(
    id: UUID,
    roles_data: UserRolesUpdate,
    token_data: Annotated[TokenData, Security(validate_token, scopes=["admin"])],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    admin_service = UserAdminService(repository)
    updated_user = await admin_service.update_user_roles(id, roles_data)
    return updated_user


@router.get("/me", response_model=UserRead)
async def get_own_user(user: Annotated[User, Depends(get_own_user)]):
    return user


@router.delete("/me", response_model=UserRead)
async def delete_own_user(
    user: Annotated[User, Depends(get_own_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    service = UserService(repository)
    if user.id is not None:
        user = await service.delete_user(user.id)
        return user
    else:
        # raise something
        pass


@router.patch("/me/password", response_model=UserRead)
async def update_own_password(
    user: Annotated[User, Depends(get_own_user)],
    password_data: UserPasswordUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repository = UserRepository(session)
    service = UserService(repository)
    if user.id is not None:
        updated_user = await service.update_user_password(user.id, password_data)
        return updated_user
    return user
