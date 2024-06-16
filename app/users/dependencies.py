from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import validate_token
from app.auth.models import TokenData
from app.database import get_session
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserAttribute
from app.users.services import UserService


async def get_own_user(
    token_data: Annotated[TokenData, Security(validate_token, scopes=["user:own"])],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Get own user.
    Args:
        token_data: Token data.
        session: The database session.
    Returns:
        A User instance representing own user.
    """
    repository = UserRepository(session)
    service = UserService(repository)
    assert token_data.username is not None
    try:
        results = await service.filter(UserAttribute.USERNAME, token_data.username)
        user: User = results[0]
    except Exception as e:
        raise e
    return user
