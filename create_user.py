"""
Create User Script

Run this script ONCE after deploying to Railway to create your first user account.

Usage:
    python create_user.py

You'll be prompted for username and password.
"""

from app import app, db
from models import User
import getpass
import sys


def create_user():
    """Create a new user account"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        print("\n=== Create New User ===\n")

        # Get username
        username = input("Enter username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            sys.exit(1)

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: User '{username}' already exists")
            sys.exit(1)

        # Get password
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("Error: Passwords do not match")
            sys.exit(1)

        if len(password) < 8:
            print("Error: Password must be at least 8 characters")
            sys.exit(1)

        # Get email (optional)
        email = input("Enter email (optional): ").strip()
        if not email:
            email = None

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"\n✓ User '{username}' created successfully!")
        print(f"\nYou can now login at your Railway URL with:")
        print(f"  Username: {username}")
        print(f"  Password: (the password you just entered)\n")


if __name__ == '__main__':
    create_user()
