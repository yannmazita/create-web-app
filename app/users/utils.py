import logging
from app.database import sessionmanager
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.users.services import UserAdminService
from app.users.repository import UserRepository

logger = logging.getLogger(__name__)


async def create_superuser():
    async with sessionmanager.session() as session:
        repository = UserRepository(session)
        admin_service = UserAdminService(repository)
        try:
            logger.info("Creating superuser with username 'admin'")
            admin_user: User = await repository.create(
                UserCreate(username="admin", password="secret")
            )
            await admin_service.update_user_roles(
                admin_user.id, UserUpdate(roles="admin")
            )
        except Exception:
            logger.warning("Failed to create")
            pass


async def create_fake_users():
    async with sessionmanager.session() as session:
        repository = UserRepository(session)
        admin_service = UserAdminService(repository)
        for i in range(40):
            try:
                fake_user: User = await repository.create(
                    UserCreate(username=f"fake_user_{i}", password="secret")
                )
                if i % 2 == 0:
                    await admin_service.update_user_roles(
                        fake_user.id,
                        UserUpdate(roles="user:own websockets"),
                    )
            except Exception:
                logger.warning(f"Failed to create fake user {i}")
                pass
