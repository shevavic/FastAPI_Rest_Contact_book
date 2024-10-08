import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import read_contacts, read_contact, create_contact, update_contact, delete_contact
from src.entity.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, username="user", password="querty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_read_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name='John', last_name='Doe', email='jdoe@example.com', phone_number='0979898998', birthday='12.12.1984'),
                    Contact(id=2, first_name='John', last_name='Smith', email='jsmthe@example.com', phone_number='0979898910', birthday='12.12.1994')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await read_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_read_contact(self):
        id = 10
        contact = [Contact(id=10, first_name='John', last_name='Doe', email='jdoe@example.com', phone_number='0979898998', birthday='12.12.1984')]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await read_contact(id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(first_name='John', last_name='Doe', email='jdoe@example.com', phone_number='0979898998', birthday='12.12.1984')
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        body = ContactUpdateSchema(first_name='John', last_name='Doe', email='jdoe@example.com', phone_number='0979898998', birthday='12.12.1984', completed=True)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=10, first_name='John', last_name='Doe', email='jd@example.com', phone_number='0979898920', birthday='12.12.1984', user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(10, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=10, first_name='John', last_name='Doe', user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(10, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)

    def tearDown(self):
        self.user = None
        self.session = None


