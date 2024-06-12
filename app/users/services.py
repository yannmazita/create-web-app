import logging
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
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
from app.users.repository import UserRepository
from app.users.schemas import UserAttribute

logger = logging.getLogger(__name__)


class UserServiceBase:
    """
    Base class for user-related operations.

    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user.
        Args:
            user: The user data.
        Returns:
            The created user.
        """
        hashed_password = get_password_hash(user.password)
        new_user = User(
            id=uuid4(), username=user.username, hashed_password=hashed_password
        )
        new_user_data = new_user.model_dump()
        created_user = await self.repository.create(new_user_data)

        return created_user

    async def delete_user(self, id: UUID) -> User:
        """
        Delete a user.
        Args:
            id: The ID of the user to delete.
        Returns:
            The deleted user.
        """
        return await self.repository.delete(id)

    async def get_users(self, offset: int = 0, limit: int = 100):
        """
        Get all users.
        Args:
            offset: The number of users to skip.
            limit: The maximum number of users to return.
        Returns:
            The list of users.
        """
        return await self.repository.all(offset, limit)


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
        try:
            logger.debug(f"Updating password for user: {user.username}")
            if not verify_password(password_data.old_password, user.hashed_password):
                logger.warning(f"Incorrect password for user: {user.username}")
                raise incorrect_password
            user.hashed_password = get_password_hash(password_data.new_password)
            self.session.add(user)
            await self.session.commit()
            logger.info(f"Password updated for user: {user.username}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e


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
            logger.debug(f"Updating username for user with {attribute.value}: {value}")
            user = await self.get_user_by_attribute(attribute, value)
            user.username = new_username.username
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(
                f"Username updated to {new_username.username} for user: {user.username}"
            )
            return user
        except NoResultFound:
            logger.warning(
                f"No user found for {attribute.value} = {value}", exc_info=False
            )
            raise user_not_found
        except MultipleResultsFound:
            logger.error(
                f"Multiple users found for {attribute.value} = {value}", exc_info=False
            )
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e

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
            logger.debug("Starting update_user_roles_by_attribute")
            user = await self.get_user_by_attribute(attribute, value)
            logger.debug(f"User found: {user}")

            user.roles = new_roles.roles
            self.session.add(user)
            logger.debug(f"User added to session: {user}")

            await self.session.commit()
            logger.debug("Session committed")

            await self.session.refresh(user)
            logger.debug("Session refreshed")
            return user
        except NoResultFound:
            logger.error("User not found", exc_info=False)
            raise user_not_found
        except MultipleResultsFound:
            logger.error("Multiple users found", exc_info=False)
            raise multiple_users_found
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred", exc_info=False)
            raise e
