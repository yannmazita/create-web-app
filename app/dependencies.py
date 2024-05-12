from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select

from app.database import get_session
from app.users.models import User

DBSessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_user_by_username(username: str) -> User:
    with Session(engine) as session:
        try:
            user = session.exec(select(User).where(User.username == username)).one()
            return user
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
            )
