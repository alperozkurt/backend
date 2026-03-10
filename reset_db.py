#!/usr/bin/env python3
"""
Drops ALL tables and recreates them with the correct schema, then seeds initial data.
Run this from /mnt/Extra/backend with the venv activated:
    python reset_db.py
"""
from app.database import engine, Base, SessionLocal
from app import models
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Recreating tables with current schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed a demo user first so we get its ID
        demo = models.User(
            email="demo@example.com",
            password=hash_password("demo123"),
            name="Demo User",
        )
        db.add(demo)
        db.commit()
        db.refresh(demo)

        # Seed financial summary bound to demo user
        summary = models.FinancialSummary(
            user_id=demo.id,
            monthly_income=1000.0,
            monthly_expense=700.0,
            monthly_savings=300.0,
        )
        db.add(summary)

        # Seed transactions bound to demo user
        transaction1 = models.Transaction(
            user_id=demo.id,
            amount=1000.0,
            description="Maaş",
            type="gelir",
            date="2026-02-02"
        )
        db.add(transaction1)

        transaction2 = models.Transaction(
            user_id=demo.id,
            amount=700.0,
            description="Gider",
            type="gider",
            date="2026-03-03"
        )
        db.add(transaction2)

        # Seed default goal bound to demo user
        goal = models.Goal(
            user_id=demo.id,
            name="Hedef",
            amount=10000.0,
            color="purple"
        )
        db.add(goal)

        db.commit()
        print(f"Done! Demo user: demo@example.com / demo123 (ID: {demo.id})")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset()
