from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    monthly_salary = Column(Float, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'gelir' or 'gider'
    date = Column(String, nullable=False)
    category = Column(String, nullable=False, default="Genel")
    is_recurring = Column(Boolean, default=False)
    currency = Column(String, nullable=False, default="TRY") # 'TRY', 'USD', 'EUR', 'GOLD'
    timestamp = Column(DateTime, default=datetime.utcnow)

class FinancialSummary(Base):
    __tablename__ = "financial_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    month = Column(String, nullable=False, default="Ocak")
    monthly_income = Column(Float, default=0.0)
    monthly_expense = Column(Float, default=0.0)
    monthly_savings = Column(Float, default=0.0)

class InvestmentProfile(Base):
    __tablename__ = "investment_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    profile = Column(String, nullable=False)  # 'korumacı', 'dengeli', 'agresif'

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    color = Column(String, nullable=False)  # e.g., 'purple', 'blue'
    category = Column(String, nullable=False, default="Genel")
    icon = Column(String, nullable=False, default="stars_rounded")
    is_completed = Column(Boolean, default=False)
    completed_at = Column(String, nullable=True)

class Saving(Base):
    __tablename__ = "savings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)  # 'TRY', 'USD', 'EUR', 'GOLD'
    description = Column(String, nullable=True)
    date = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SavedExpense(Base):
    __tablename__ = "saved_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False, default="Genel")