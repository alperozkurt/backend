from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from typing import List

router = APIRouter(prefix="/api", tags=["financial"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Financial Summary Endpoints
@router.get("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def get_financial_summary(db: Session = Depends(get_db)):
    summary = db.query(models.FinancialSummary).first()
    if not summary:
        # Create default summary if none exists
        summary = models.FinancialSummary(
            monthly_income=8500.0,
            monthly_expense=3250.0,
            monthly_savings=5250.0
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return summary

@router.put("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def update_financial_summary(
    summary_update: schemas.FinancialSummaryUpdate,
    db: Session = Depends(get_db)
):
    summary = db.query(models.FinancialSummary).first()
    if not summary:
        summary = models.FinancialSummary()
        db.add(summary)

    update_data = summary_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(summary, field, value)

    db.commit()
    db.refresh(summary)
    return summary

# Transaction Endpoints
@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    income = db.query(models.Transaction).filter(models.Transaction.type == "gelir").all()
    expenses = db.query(models.Transaction).filter(models.Transaction.type == "gider").all()

    # Mock activities - in a real app, you'd have an activities table
    activities = []
    for transaction in income + expenses:
        activities.append({
            "date": transaction.date,
            "type": transaction.type,
            "amount": transaction.amount,
            "description": transaction.description
        })

    return {
        "income": [{"amount": t.amount, "description": t.description, "date": t.date} for t in income],
        "expenses": [{"amount": t.amount, "description": t.description, "date": t.date} for t in expenses],
        "activities": activities
    }

@router.post("/transactions")
def add_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    if transaction.type not in ["gelir", "gider"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    db_transaction = models.Transaction(
        amount=transaction.amount,
        description=transaction.description,
        type=transaction.type,
        date=transaction.date
    )
    db.add(db_transaction)

    # Update financial summary
    summary = db.query(models.FinancialSummary).first()
    if not summary:
        summary = models.FinancialSummary()
        db.add(summary)

    if transaction.type == "gelir":
        summary.monthly_income += transaction.amount
    elif transaction.type == "gider":
        summary.monthly_expense += transaction.amount

    summary.monthly_savings = summary.monthly_income - summary.monthly_expense

    db.commit()
    return {"message": "Transaction added successfully"}

# Investment Profile Endpoints
@router.get("/investment/profile")
def get_investment_profile(db: Session = Depends(get_db)):
    profile = db.query(models.InvestmentProfile).first()
    return {"profile": profile.profile if profile else None}

@router.post("/investment/profile")
def save_investment_profile(
    profile: schemas.InvestmentProfileCreate,
    db: Session = Depends(get_db)
):
    if profile.profile not in ["korumacı", "dengeli", "agresif"]:
        raise HTTPException(status_code=400, detail="Invalid profile type")

    db_profile = db.query(models.InvestmentProfile).first()
    if not db_profile:
        db_profile = models.InvestmentProfile(profile=profile.profile)
        db.add(db_profile)
    else:
        db_profile.profile = profile.profile

    db.commit()
    return {"profile": profile.profile}

# User Profile Endpoints
@router.get("/user/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        user = models.User(name="")
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"name": user.name}

@router.put("/user/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    profile: schemas.UserProfileUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).first()
    if not user:
        user = models.User(name=profile.name)
        db.add(user)
    else:
        user.name = profile.name

    db.commit()
    db.refresh(user)
    return {"name": user.name}