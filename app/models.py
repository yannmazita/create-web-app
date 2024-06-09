from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import SQLModel


class Base(AsyncAttrs, SQLModel):
    pass
