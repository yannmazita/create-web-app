from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_routes
from app.clients import router as client_routes
from app.config import settings
from app.database import create_db_and_tables, sessionmanager
from app.users import router as user_routes
from app.users.utils import create_fake_users, create_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    create_superuser()
    create_fake_users()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(auth_routes.router)
api.include_router(client_routes.router)
api.include_router(user_routes.router)


def start_server():
    uvicorn.run(
        "app.main:api",
        host=settings.app_host,
        port=int(settings.app_port),
        log_level="info",
    )
    # when reload=true, the 1st argument the location of main as module and a string
    # ie: "app.main:api"


if __name__ == "__main__":
    start_server()
