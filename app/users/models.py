from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base


class UserBase(Base):
    username: Mapped[str] = mapped_column(index=True, unique=True)


class User(Base):
    __tablename__ = "users"
    hashed_password: Mapped[str] = mapped_column()
    roles: Mapped[str] = mapped_column(default="")
