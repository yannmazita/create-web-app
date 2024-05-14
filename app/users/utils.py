from app.database import sessionmanager
from app.users.models import UserCreate, UserRolesUpdate
from app.users.schemas import UserAttribute
from app.users.services import UserAdminService, UserService


async def create_superuser():
    async with sessionmanager.session() as session:
        service = UserService(session)
        admin_user = UserCreate(username="admin", password="secret")
        try:
            await service.create_user(admin_user)
        except Exception as e:
            pass
        admin_service = UserAdminService(session)
        await admin_service.update_user_roles_by_attribute(
            UserAttribute.USERNAME, "admin", UserRolesUpdate(roles="admin")
        )


async def create_fake_users():
    async with sessionmanager.session() as session:
        service = UserService(session)
        for i in range(40):
            user: UserCreate = UserCreate(
                username=f"fake_user_{i}",
                password="secret",
            )
            try:
                await service.create_user(user)
            except Exception as e:
                pass
            if i % 2 == 0:
                admin_service = UserAdminService(session)
                try:
                    await admin_service.update_user_roles_by_attribute(
                        UserAttribute.USERNAME,
                        f"fake_user_{i}",
                        UserRolesUpdate(roles="user:own websockets"),
                    )
                except Exception as e:
                    pass
