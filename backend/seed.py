"""Seed script — creates initial admin user and tenant."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.connection import async_session_factory
from src.database.models import Tenant, User
from src.utils.security import hash_password
from sqlalchemy import select


async def seed():
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == "admin@polis.com"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        tenant = Tenant(name="Polis", is_active=True)
        db.add(tenant)
        await db.flush()

        user = User(
            tenant_id=tenant.id,
            name="Admin",
            email="admin@polis.com",
            password_hash=hash_password("admin123"),
            is_admin=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.commit()

        print(f"✅ Tenant created: {tenant.id}")
        print(f"✅ Admin user created: {user.id}")
        print("   Email: admin@polis.com")
        print("   Password: admin123")


if __name__ == "__main__":
    asyncio.run(seed())
