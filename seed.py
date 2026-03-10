#!/usr/bin/env python3
"""
Seed script to populate the database with initial mock data for GençCüzdan
"""
from app.database import engine, Base, SessionLocal
from app.models import Transaction, FinancialSummary, InvestmentProfile, User

def seed_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(FinancialSummary).first():
            print("Database already seeded")
            return

        # Create financial summary
        summary = FinancialSummary(
            monthly_income=8500.0,
            monthly_expense=3250.0,
            monthly_savings=5250.0
        )
        db.add(summary)

        # Create initial transactions
        transactions_data = [
            # Income
            {"amount": 5000, "description": "Maaş", "type": "gelir", "date": "Bu Ay"},
            {"amount": 1500, "description": "Ek gelir", "type": "gelir", "date": "Bu Ay"},
            {"amount": 2000, "description": "Bonus", "type": "gelir", "date": "Geçen Ay"},
            # Expenses
            {"amount": 1200, "description": "Kira", "type": "gider", "date": "Bu Ay"},
            {"amount": 450, "description": "Yemek", "type": "gider", "date": "Bu Ay"},
            {"amount": 600, "description": "Ulaşım", "type": "gider", "date": "Bu Ay"},
            {"amount": 1000, "description": "Alışveriş", "type": "gider", "date": "Geçen Ay"},
        ]

        for tx_data in transactions_data:
            transaction = Transaction(**tx_data)
            db.add(transaction)

        # Create default user profile
        user = User(name="")
        db.add(user)

        db.commit()
        print("Database seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()