import logging
from uuid import UUID, uuid4

from app.auth.exceptions import incorrect_password
from app.auth.utils import get_password_hash, verify_password
from app.users.models import (
    User,
)
from app.users.repository import UserRepository
from app.users.schemas import (
    User as UserSchema,
)
from app.users.schemas import (
    UserCreate,
    UserPasswordUpdate,
    UserRolesUpdate,
    UserUpdate,
    UserUsernameUpdate,
)

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
        new_user = UserSchema(
            id=uuid4(), username=user.username, hashed_password=hashed_password
        )
        created_user = await self.repository.create(new_user)

        return created_user

    async def get_user(self, id: UUID) -> User:
        """
        Get a user by ID.
        Args:
            id: The ID of the user.
        Returns:
            The user.
        """
        return await self.repository.get_by_attribute(id)

    async def update_user(self, id: UUID, data: UserUpdate) -> User:
        """
        Update a user.
        Args:
            id: The ID of the user to update.
            data: The updated user data.
        Returns:
            The updated user.
        """
        return await self.repository.update_by_attribute(data, id)

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
        return await self.repository.get_all(offset, limit)


class UserService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def update_user_password(
        self, id: UUID, password_data: UserPasswordUpdate
    ) -> None:
        """
        Update a user's password.
        Args:
            id: The ID of the user.
            password_data: The new password data.
        """
        logger.debug(f"Updating password for user with ID: {id}")
        user: User = await self.repository.get(id)
        if not verify_password(password_data.old_password, user.hashed_password):
            logger.warning(f"Incorrect password for user: {user.username}")
            raise incorrect_password
        updated_user = user.model_copy()
        updated_user.hashed_password = get_password_hash(password_data.new_password)
        if user.id is not None:
            await self.repository.update(user.id, updated_user.model_dump())
        else:
            # raise something?
            logger.error("User ID is None", exc_info=False)
        logger.info(f"Password updated for user: {user.username}")


class UserAdminService(UserServiceBase):
    """
    Class for user-related operations.
    Attributes:
        repository: The user repository to be used for operations.
    """

    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def update_user_username(
        self, id: UUID, new_username: UserUsernameUpdate
    ) -> User:
        """
        Update a user's username.
        Args:
            id: The ID of the user.
            new_username: The new username.
        Returns:
            The updated user.
        """
        logger.debug(f"Updating username for user with ID: {id}")
        user: User = await self.repository.get(id)
        updated_user = user.model_copy()
        updated_user.username = new_username.username
        assert user.id is not None
        await self.repository.update(user.id, updated_user.model_dump())
        logger.error("User ID is None", exc_info=False)
        logger.info(
            f"Username updated to {new_username.username} for user: {user.username}"
        )
        return user

    async def update_user_roles(self, id: UUID, new_roles: UserRolesUpdate) -> User:
        """
        Update a user's roles.
        Args:
            user: The user.
            new_roles: The new roles.
        Returns:
            The updated user.
        """
        logger.debug(f"Updating roles for user with ID: {id}")
        user: User = await self.repository.get(id)
        updated_user = user.model_copy()
        updated_user.roles = new_roles.roles
        if user.id is not None:
            await self.repository.update(user.id, updated_user.model_dump())
        else:
            # raise something?
            logger.error("User ID is None", exc_info=False)
        logger.info(f"Roles updated for user: {user.username}")
        return user
