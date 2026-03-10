from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'gelir' or 'gider'
    date = Column(String, nullable=False)

class FinancialSummary(Base):
    __tablename__ = "financial_summary"

    id = Column(Integer, primary_key=True, index=True)
    monthly_income = Column(Float, default=0.0)
    monthly_expense = Column(Float, default=0.0)
    monthly_savings = Column(Float, default=0.0)

class InvestmentProfile(Base):
    __tablename__ = "investment_profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile = Column(String, nullable=False)  # 'korumacı', 'dengeli', 'agresif'