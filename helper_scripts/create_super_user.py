#!/usr/bin/env python
"""
Script to create a superuser (admin) without requiring authentication.
This script should be run from the command line.

Usage:
    python create_super_user.py --email admin@example.com --password securepassword --first_name Admin --last_name User
"""


import argparse
import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select  # noqa:

from app.db.db_init import get_session_for_script  # noqa:
from app.db.models.user import User, UserRole  # noqa:


async def create_superuser(email: str, password: str, first_name: str = None, last_name: str = None) -> None:
    """
    Create a superuser (admin) in the database.

    Args:
        email: Email address for the superuser
        password: Password for the superuser
        first_name: First name for the superuser (optional)
        last_name: Last name for the superuser (optional)
    """
    # Get a database session
    async for db in get_session_for_script():
        # Check if a user with this email already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()

        if existing_user:
            print(f"User with email '{email}' already exists.")
            if existing_user.role == UserRole.ADMIN:
                print("This user already has admin privileges.")
                return
            else:
                # Update the existing user to have admin role
                print(f"Updating user '{email}' to have admin privileges.")
                existing_user.role = UserRole.ADMIN
                await db.commit()
                print(f"User '{email}' has been updated to admin role.")
                return

        # Create new admin user
        user = User(
            email=email,
            password=password,  # Password will be hashed in User.__init__
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,  # Automatically verify admin users
        )

        db.add(user)
        await db.commit()
        print(f"Superuser '{email}' created successfully with admin privileges.")


def main():
    """Parse command line arguments and create a superuser."""
    parser = argparse.ArgumentParser(description="Create a superuser (admin) account")
    parser.add_argument("--email", required=True, help="Email address for the superuser")
    parser.add_argument("--password", required=True, help="Password for the superuser")
    parser.add_argument("--first_name", help="First name for the superuser")
    parser.add_argument("--last_name", help="Last name for the superuser")

    args = parser.parse_args()

    # Run the async function
    asyncio.run(
        create_superuser(email=args.email, password=args.password, first_name=args.first_name, last_name=args.last_name)
    )


if __name__ == "__main__":
    main()


# Usage:
# uv run helper_scripts/create_super_user.py --email admin@example.com --password securepassword --first_name Admin --last_name User
# uv run helper_scripts/create_super_user.py --email rajathkumarks@gmail.com --password securepassword --first_name Rajath --last_name Kumar
