import os
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import UUIDIDMixin, BaseUserManager, FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.db.session import get_user_db
from app.models.user import User

JWT_SECRET = os.getenv("JWT_SECRET")

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = JWT_SECRET
    verification_token_secret = JWT_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
