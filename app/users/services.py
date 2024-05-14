from uuid import uuid4

from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.auth.exceptions import incorrect_password
from app.auth.utils import get_password_hash, verify_password
from app.users.exceptions import (
    multiple_users_found,
    user_already_exists,
    user_not_found,
)
from app.users.models import (
    User,
    UserCreate,
    UserPasswordUpdate,
    UserRolesUpdate,
    UserUsernameUpdate,
)
from app.users.schemas import UserAttribute


class UserServiceBase:
    """
    Base class for user-related operations.

    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user.
        Args:
            user: The user data.
        Returns:
            The created user.
        """
        try:
            query = select(User).where(User.username == user.username)
            response = await self.session.execute(query)
            raise user_already_exists
        except NoResultFound:
            pass

        hashed_password = get_password_hash(user.password)
        new_user = User(
            id=uuid4(), username=user.username, hashed_password=hashed_password
        )
        db_user = User.model_validate(new_user)
        try:
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
        except IntegrityError as e:
            raise e

        return db_user

    async def get_user_by_attribute(self, attribute: UserAttribute, value: str) -> User:
        """
        Get a user by a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The user with the specified attribute and value.
        """
        try:
            query = select(User).where(getattr(User, attribute.value) == value)
            response = await self.session.execute(query)
        except MultipleResultsFound:
            raise multiple_users_found
        except NoResultFound:
            raise user_not_found
        return response.scalar_one()

    async def update_user_by_attribute(
        self, attribute: UserAttribute, value: str, user: UserCreate
    ) -> User:
        """
        Update a user using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            user: The new user data.
        Returns:
            The updated user.
        """
        try:
            user_db = await self.get_user_by_attribute(attribute, value)
            user_data = user.model_dump()
            for key, value in user_data.items():
                setattr(user_db, key, value)
            self.session.add(user_db)
            await self.session.commit()
            await self.session.refresh(user_db)
        except NoResultFound:
            raise user_not_found
        except MultipleResultsFound:
            raise multiple_users_found

        return user_db

    async def delete_user(self, user: User) -> User:
        """
        Delete a user.
        Args:
            user: The user to delete.
        Returns:
            The deleted user.
        """
        try:
            await self.session.delete(user)
            await self.session.commit()
        except NoResultFound:
            raise user_not_found

        return user

    async def delete_user_by_attribute(
        self, attribute: UserAttribute, value: str
    ) -> User:
        """
        Delete a user using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
        Returns:
            The deleted user.
        """
        try:
            user = await self.get_user_by_attribute(attribute, value)
            await self.session.delete(user)
            await self.session.commit()
        except NoResultFound:
            raise user_not_found
        except MultipleResultsFound:
            raise multiple_users_found

        return user

    async def get_users(self, offset: int = 0, limit: int = 100):
        """
        Get all users.
        Args:
            offset: The number of users to skip.
            limit: The maximum number of users to return.
        Returns:
            The list of users.
        """
        total_count_query = select(func.count()).select_from(User)
        total_count_response = await self.session.execute(total_count_query)
        total_count: int = total_count_response.scalar_one()

        try:
            users_query = select(User).offset(offset).limit(limit)
            users_response = await self.session.execute(users_query)
            users = users_response.scalars().all()
        except NoResultFound:
            raise user_not_found
        return users, total_count


class UserService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_user_password(
        self, user: User, password_data: UserPasswordUpdate
    ) -> None:
        """
        Update a user's password.
        Args:
            user: The user.
            password_data: The new password data.
        """
        if not verify_password(password_data.old_password, user.hashed_password):
            raise incorrect_password
        else:
            user.hashed_password = get_password_hash(password_data.new_password)
            self.session.add(user)
            await self.session.commit()


class UserAdminService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        session: The database session to be used for operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_user_username_by_attribute(
        self, attribute: UserAttribute, value: str, new_username: UserUsernameUpdate
    ) -> User:
        """
        Update a user's username using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            new_username: The new username.
        Returns:
            The updated user.
        """
        try:
            user = await self.get_user_by_attribute(attribute, value)
            user.username = new_username.username
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except NoResultFound:
            raise user_not_found
        except MultipleResultsFound:
            raise multiple_users_found

    async def update_user_roles_by_attribute(
        self, attribute: UserAttribute, value: str, new_roles: UserRolesUpdate
    ) -> User:
        """
        Update a user's roles using a specified attribute.
        Args:
            attribute: The attribute to filter by.
            value: The value to filter by.
            new_roles: The new roles.
        Returns:
            The updated user.
        """
        try:
            user = await self.get_user_by_attribute(attribute, value)
            user.roles = new_roles.roles
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except NoResultFound:
            raise user_not_found
        except MultipleResultsFound:
            raise multiple_users_found
