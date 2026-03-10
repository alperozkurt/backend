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
        # Seed financial summary
        summary = models.FinancialSummary(
            monthly_income=0.0,
            monthly_expense=0.0,
            monthly_savings=0.0,
        )
        db.add(summary)

        # Seed a demo user (can register via the app too)
        demo = models.User(
            email="demo@example.com",
            password=hash_password("demo123"),
            name="Demo User",
        )
        db.add(demo)

        db.commit()
        print("Done! Demo user: demo@example.com / demo123")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset()
