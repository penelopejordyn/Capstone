import unittest
from app import app, db
from models import User


def test_register_user(self):
        # Test user registration
        response = self.app.post('/register', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)

def test_authenticate_user(self):
        # Test user authentication
        self.test_register_user()  # First, register a user
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'Welcome, testuser', response.data)

if __name__ == '__main__':
    unittest.main()