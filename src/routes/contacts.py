from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repositories_contacts
from src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contacts(
        limit: int = Query(10, ge=10, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """Retrieve a list of contacts.

    :param limit: Maximum number of contacts to return (default 10, max 500).
    :type limit: int
    :param offset: Number of contacts to skip (default 0).
    :type offset: int
    :param db: Database session object.
    :type db: AsyncSession, optional
    :param user: Current user.
    :type user: User
    :return: List of contacts.
    :rtype: list[ContactResponse]
    """
    contacts = await repositories_contacts.read_contacts(
        limit=limit, offset=offset, db=db, user=user
    )
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contact(
        contact_id: int = Path(..., title="The ID of the contact to retrieve"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """Retrieve a single contact by ID.

    :param contact_id: The ID of the contact.
    :type contact_id: int
    :param db: Database session object.
    :type db: AsyncSession, optional
    :param user: Current user.
    :type user: User
    :raises HTTPException: If contact is not found.
    :return: The contact.
    :rtype: ContactResponse
    """
    contact = await repositories_contacts.read_contact(
        contact_id=contact_id, db=db, user=user
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def create_contact(
        body: ContactSchema,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """Create a new contact.

    :param body: Data for the new contact.
    :type body: ContactSchema
    :param db: Database session object.
    :type db: AsyncSession, optional
    :param user: Current user.
    :type user: User
    :return: The created contact.
    :rtype: ContactResponse
    """
    contact = await repositories_contacts.create_contact(body=body, db=db, user=user)
    return contact


@router.put("/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(
        body: ContactUpdateSchema,
        contact_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """Update an existing contact.

        :param contact_id: The ID of the contact.
        :type contact_id: int
        :param body: Data to update the contact.
        :type body: ContactUpdateSchema
        :param db: Database session object.
        :type db: AsyncSession, optional
        :param user: Current user.
        :type user: User
        :raises HTTPException: If contact is not found.
        :return: The updated contact.
        :rtype: ContactResponse
        """
    contact = await repositories_contacts.update_contact(
        contact_id, body=body, db=db, user=user
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_contact(
        contact_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """Delete a contact.

        :param contact_id: The ID of the contact.
        :type contact_id: int
        :param db: Database session object.
        :type db: AsyncSession, optional
        :param user: Current user.
        :type user: User
        """
    contact = await repositories_contacts.delete_contact(contact_id, db=db, user=user)
    return contact
