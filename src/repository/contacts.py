from datetime import datetime, timedelta

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema


async def read_contacts(limit: int, offset: int, db: AsyncSession):
    """Returns a list of user contacts.

    :param limit: Maximum number of contacts to return.
    :type limit: int
    :param offset: Result offset for pagination tracking.
    :type offset: int
    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom contacts are being fetched.
    :type user: User
    :return: List of user contacts.
    :rtype: List[Contact]
    """
    stmt = select(Contact).offset(offset).limit(limit)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def read_contact(contact_id: int, db: AsyncSession, user: User):
    """Returns a contact by its ID.

    :param contact_id: ID of the contact to search for.
    :type contact_id: int
    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom the contact is being searched.
    :type user: User
    :return: Contact object or None if contact is not found.
    :rtype: Optional[Contact]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """Creates a new contact for the user.

    :param body: Data of the new contact.
    :type body: ContactSchema
    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom the contact is being created.
    :type user: User
    :return: Created contact.
    :rtype: Contact
    """
    stmt = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User
):
    """Updates an existing contact by its ID.

    :param contact_id: ID of the contact to update.
    :type contact_id: int
    :param body: Data for updating the contact.
    :type body: ContactUpdateSchema
    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom the contact is being updated.
    :type user: User
    :return: Updated contact or None if contact is not found.
    :rtype: Optional[Contact]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.completed = body.completed
        await db.commit()
        await db.refresh(contact)
        return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """Deletes a contact by its ID.

    :param contact_id: ID of the contact to delete.
    :type contact_id: int
    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom the contact is being deleted.
    :type user: User
    :return: Deleted contact or None if contact is not found.
    :rtype: Optional[Contact]
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
        return contact


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    """Returns a list of contacts with upcoming birthdays.

    :param db: Database session object.
    :type db: AsyncSession
    :param user: User object for whom contacts with upcoming birthdays are being fetched.
    :type user: User
    :return: List of contacts with upcoming birthdays.
    :rtype: List[Contact]
    """
    today = datetime.now().date()
    next_week = today + timedelta(days=7)

    stmt = (
        select(Contact)
        .filter_by(user=user)
        .where(
            (extract("month", Contact.birthday) == today.month)
            & (extract("day", Contact.birthday) >= today.day)
        )
        | (
            (extract("month", Contact.birthday) == next_week.month)
            & (extract("day", Contact.birthday) < today.day)
        )
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts
