from enum import Enum
from uuid import UUID

from pydantic import BaseModel, validate_call

from app.auth.config import OAUTH_SCOPES


class UserAttribute(Enum):
    ID = "id"
    USERNAME = "username"


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    roles: str


class Users(BaseModel):
    users: list[UserRead]
    total: int


class UserUsernameUpdate(BaseModel):
    username: str

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_username()

    def validate_username(self):
        # add these constants to local config.py
        if len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(self.username) > 50:
            raise ValueError("Username must be at most 50 characters")


class UserRolesUpdate(BaseModel):
    roles: str

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_roles()

    def validate_roles(self):
        valid_roles = set(OAUTH_SCOPES.keys())
        given_roles = set(self.roles.split())
        if not given_roles.issubset(valid_roles):
            raise ValueError(f"Invalid roles: {given_roles - valid_roles}")


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_passwords()

    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if self.old_password == self.new_password:
            raise ValueError("New password is the same as the old password")
