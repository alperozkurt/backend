from fastapi import APIRouter, Depends, HTTPException, Header
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

# Temporary custom auth: requires X-User-Id header
def get_current_user_id(x_user_id: int = Header(None)):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")
    return x_user_id


# Financial Summary Endpoints
@router.get("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def get_financial_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        # Create default summary if none exists for this user
        summary = models.FinancialSummary(
            user_id=user_id,
            monthly_income=0.0,
            monthly_expense=0.0,
            monthly_savings=0.0
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return summary

@router.put("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def update_financial_summary(
    summary_update: schemas.FinancialSummaryUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        summary = models.FinancialSummary(user_id=user_id)
        db.add(summary)

    update_data = summary_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(summary, field, value)

    db.commit()
    db.refresh(summary)
    return summary


# Transaction Endpoints
@router.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    income = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "gelir"
    ).all()
    expenses = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "gider"
    ).all()

    # Activities list combines income and expenses
    activities = []
    for transaction in income + expenses:
        activities.append({
            "date": transaction.date,
            "type": transaction.type,
            "amount": transaction.amount,
            "description": transaction.description
        })

    # Sort activities by date descending (simple string sort works for YYYY-MM-DD)
    activities.sort(key=lambda x: x["date"], reverse=True)

    return {
        "income": [{"amount": t.amount, "description": t.description, "date": t.date} for t in income],
        "expenses": [{"amount": t.amount, "description": t.description, "date": t.date} for t in expenses],
        "activities": activities
    }

@router.post("/transactions")
def add_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if transaction.type not in ["gelir", "gider"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    db_transaction = models.Transaction(
        user_id=user_id,
        amount=transaction.amount,
        description=transaction.description,
        type=transaction.type,
        date=transaction.date
    )
    db.add(db_transaction)

    # Update financial summary
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        summary = models.FinancialSummary(user_id=user_id)
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
def get_investment_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    profile = db.query(models.InvestmentProfile).filter(models.InvestmentProfile.user_id == user_id).first()
    return {"profile": profile.profile if profile else None}

@router.post("/investment/profile")
def save_investment_profile(
    profile: schemas.InvestmentProfileCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if profile.profile not in ["korumacı", "dengeli", "agresif"]:
        raise HTTPException(status_code=400, detail="Invalid profile type")

    db_profile = db.query(models.InvestmentProfile).filter(models.InvestmentProfile.user_id == user_id).first()
    if not db_profile:
        db_profile = models.InvestmentProfile(user_id=user_id, profile=profile.profile)
        db.add(db_profile)
    else:
        db_profile.profile = profile.profile

    db.commit()
    return {"profile": profile.profile}


# Goal Endpoints
@router.get("/goals", response_model=schemas.GoalResponse)
def get_goal(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.user_id == user_id).first()
    if not goal:
        goal = models.Goal(
            user_id=user_id,
            name="🎯 Hedef",
            amount=10000.0,
            color="purple"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal

@router.put("/goals", response_model=schemas.GoalResponse)
def update_goal(
    goal_update: schemas.GoalCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.user_id == user_id).first()
    if not goal:
        goal = models.Goal(user_id=user_id, name=goal_update.name, amount=goal_update.amount, color=goal_update.color)
        db.add(goal)
    else:
        goal.name = goal_update.name
        goal.amount = goal_update.amount
        goal.color = goal_update.color

    db.commit()
    db.refresh(goal)
    return goal


# User Profile Endpoints
@router.get("/user/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": user.name or ""}

@router.put("/user/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    profile: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = profile.name
    db.commit()
    db.refresh(user)
    return {"name": user.name}