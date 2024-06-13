from app.repository import DatabaseRepository
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.users.models import User


class UserRepository(DatabaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
