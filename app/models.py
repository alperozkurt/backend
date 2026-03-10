from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'gelir' or 'gider'
    date = Column(String, nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    color = Column(String, nullable=False)  # e.g., 'purple', 'blue'