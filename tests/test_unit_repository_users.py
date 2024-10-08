import unittest
from unittest.mock import AsyncMock, patch
import asyncio

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar_url


class TestUserRepository(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    @patch('src.repository.users.get_db')
    async def test_get_user_by_email(self, mock_get_db):
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.execute.return_value.scalar_one_or_none.return_value = User(email='test@example.com')
        user = await get_user_by_email('test@example.com')
        self.assertEqual(user.email, 'test@example.com')
        mock_get_db.assert_called_once()
        mock_db.execute.assert_called_once()

    @patch('src.repository.users.get_db')
    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, mock_gravatar, mock_get_db):
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_gravatar.return_value.get_image.return_value = 'avatar_url'
        user = await create_user(UserSchema(email='test@example.com', password='password'))
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.avatar, 'avatar_url')
        mock_get_db.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('src.repository.users.get_db')
    async def test_update_token(self, mock_get_db):
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        user = User(email='test@example.com')
        await update_token(user, 'new_token')
        self.assertEqual(user.refresh_token, 'new_token')
        mock_db.commit.assert_called_once()

    @patch('src.repository.users.get_db')
    @patch('src.repository.users.get_user_by_email')
    async def test_confirmed_email(self, mock_get_user_by_email, mock_get_db):
        # Arrange
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_user = User(email='test@example.com')
        mock_get_user_by_email.return_value = mock_user
        await confirmed_email('test@example.com')
        self.assertTrue(mock_user.confirmed)
        mock_get_user_by_email.assert_called_once_with('test@example.com', mock_db)
        mock_db.commit.assert_called_once()

    @patch('src.repository.users.get_db')
    @patch('src.repository.users.get_user_by_email')
    async def test_update_avatar_url(self, mock_get_user_by_email, mock_get_db):
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_user = User(email='test@example.com')
        mock_get_user_by_email.return_value = mock_user
        user = await update_avatar_url('test@example.com', 'new_avatar_url')
        self.assertEqual(user.avatar, 'new_avatar_url')
        mock_get_user_by_email.assert_called_once_with('test@example.com', mock_db)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)




