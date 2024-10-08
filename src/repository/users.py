from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a user by their email address.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: Database session object.
    :type db: AsyncSession, optional
    :return: The user object corresponding to the given email, or None if no user found.
    :rtype: User
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """Create a new user.

    :param body: Data of the new user.
    :type body: UserSchema
    :param db: Database session object.
    :type db: AsyncSession, optional
    :return: The newly created user object.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """Update the refresh token of a user.

    :param user: The user object to update.
    :type user: User
    :param token: The new refresh token value.
    :type token: str, optional
    :param db: Database session object.
    :type db: AsyncSession
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    """Mark a user's email as confirmed.

    :param email: The email address of the user.
    :type email: str
    :param db: Database session object.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession):
    """Update the avatar URL of a user.

    :param email: The email address of the user.
    :type email: str
    :param url: The new avatar URL.
    :type url: str, optional
    :param db: Database session object.
    :type db: AsyncSession
    :return: The updated user object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
