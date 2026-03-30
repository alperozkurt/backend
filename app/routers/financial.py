from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import SessionLocal
from .. import models, schemas
from typing import List, Optional

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


import urllib.request
import json
import time

# Currency Rates Caching
CURRENCY_RATES_DATA = {
    "USD/TL": 44.36, "EUR/TL": 51.45, "GBP/TL": 56.20, "JPY/TL": 0.296,
    "CHF/TL": 50.10, "CNY/TL": 6.10,
    "Gram Altın": 6500.0, "Gümüş": 55.0,
    "BTC/TL": 3160000.0, "ETH/TL": 72000.0,
    "TRY": 1.0
}
LAST_UPDATED_TIME = 0.0

def fetch_live_rates():
    global LAST_UPDATED_TIME, CURRENCY_RATES_DATA
    current_time = time.time()
    if current_time - LAST_UPDATED_TIME < 1800:  # 30 min cache
        return CURRENCY_RATES_DATA

    usd_try = CURRENCY_RATES_DATA.get("USD/TL", 44.36)

    # 1) Fiat currencies from ExchangeRate API (returns 150+ currencies)
    try:
        req = urllib.request.Request("https://open.er-api.com/v6/latest/USD", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode())
            if data.get("result") == "success":
                rates = data.get("rates", {})
                usd_try = float(rates.get("TRY", 44.36))
                eur_usd = float(rates.get("EUR", 0.86)) or 1.0
                gbp_usd = float(rates.get("GBP", 0.79)) or 1.0
                jpy_usd = float(rates.get("JPY", 149.5)) or 1.0
                chf_usd = float(rates.get("CHF", 0.88)) or 1.0
                cny_usd = float(rates.get("CNY", 7.24)) or 1.0

                CURRENCY_RATES_DATA["USD/TL"] = usd_try
                CURRENCY_RATES_DATA["EUR/TL"] = round(usd_try / eur_usd, 4) if eur_usd else 51.0
                CURRENCY_RATES_DATA["GBP/TL"] = round(usd_try / gbp_usd, 4) if gbp_usd else 56.0
                CURRENCY_RATES_DATA["JPY/TL"] = round(usd_try / jpy_usd, 4) if jpy_usd else 0.30
                CURRENCY_RATES_DATA["CHF/TL"] = round(usd_try / chf_usd, 4) if chf_usd else 50.0
                CURRENCY_RATES_DATA["CNY/TL"] = round(usd_try / cny_usd, 4) if cny_usd else 6.1
                CURRENCY_RATES_DATA["TRY"] = 1.0
                print(f"[rates] Exchange: USD/TL={usd_try}, EUR/TL={CURRENCY_RATES_DATA['EUR/TL']}, GBP/TL={CURRENCY_RATES_DATA['GBP/TL']}")
    except Exception as e:
        print(f"[rates] Exchange API error: {e}")

    # 2) BTC, ETH, Gold, Silver from CoinGecko
    try:
        cg_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,pax-gold&vs_currencies=try,usd"
        req2 = urllib.request.Request(cg_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req2, timeout=10) as response:
            raw = response.read().decode()
            print(f"[rates] CoinGecko raw: {raw[:300]}")
            cg_data = json.loads(raw)

            btc_try = cg_data.get("bitcoin", {}).get("try")
            if btc_try is not None:
                CURRENCY_RATES_DATA["BTC/TL"] = float(btc_try)
                print(f"[rates] BTC/TL={btc_try}")

            eth_try = cg_data.get("ethereum", {}).get("try")
            if eth_try is not None:
                CURRENCY_RATES_DATA["ETH/TL"] = float(eth_try)
                print(f"[rates] ETH/TL={eth_try}")

            xau_usd = cg_data.get("pax-gold", {}).get("usd")
            if xau_usd is not None:
                gram_try = round((float(xau_usd) / 31.1035) * usd_try, 2)
                CURRENCY_RATES_DATA["Gram Altın"] = gram_try
                # Silver approximation: ~1/80th of gold price
                CURRENCY_RATES_DATA["Gümüş"] = round(gram_try / 80, 2)
                print(f"[rates] Gram Altın={gram_try} (XAU/oz=${xau_usd}), Gümüş={CURRENCY_RATES_DATA['Gümüş']}")
    except Exception as e:
        print(f"[rates] CoinGecko error: {e}")

    LAST_UPDATED_TIME = current_time
    print(f"[rates] Final: {CURRENCY_RATES_DATA}")
    return CURRENCY_RATES_DATA



def get_exchange_rates():
    return fetch_live_rates()

def convert_to_try(amount: float, currency: str) -> float:
    rates = get_exchange_rates()
    # Handle mappings from frontend dropdown values to backend rate keys
    curr = currency.upper()
    mapping = {
        'USD': 'USD/TL',
        'EUR': 'EUR/TL',
        'GOLD': 'Gram Altın',
        'GRAM ALTIN': 'Gram Altın',
        'BTC': 'BTC/TL',
        'BTC/TL': 'BTC/TL',
        'TRY': 'TRY'
    }
    key = mapping.get(curr, curr)
    rate = rates.get(key, 1.0)
    return amount * rate


@router.get("/market/rates")
def get_market_rates():
    return get_exchange_rates()


# Financial Summary Endpoints
@router.get("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def get_financial_summary(
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    months_tr = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    current_month_index = datetime.now().month - 1
    
    if not month:
        month = months_tr[current_month_index]
    
    # Calculate totals from transactions for THIS month
    year = datetime.now().year
    month_int = months_tr.index(month) + 1
    date_prefix = f"{year}-{month_int:02d}"
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.date.startswith(date_prefix)
    ).all()
    
    total_income = 0.0
    total_expense = 0.0
    
    for t in transactions:
        amount_try = convert_to_try(t.amount, t.currency)
        if t.type == "gelir":
            total_income += amount_try
        elif t.type == "gider":
            total_expense += amount_try
            
    # Calculate savings (derived value for the month)
    monthly_savings = total_income - total_expense
    
    return {
        "month": month,
        "monthly_income": total_income,
        "monthly_expense": total_expense,
        "monthly_savings": monthly_savings
    }


@router.put("/financial/summary", response_model=schemas.FinancialSummaryResponse)
def update_financial_summary(
    summary_update: schemas.FinancialSummaryUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # This endpoint is now less critical as GET calculates everything,
    # but we'll return the same calculated data for compatibility.
    return get_financial_summary(summary_update.month, db, user_id)


# Transaction Endpoints
@router.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    year: Optional[int] = None,
    month: Optional[int] = None
):
    query_income = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "gelir"
    )
    query_expenses = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "gider"
    )

    if year and month:
        date_prefix = f"{year}-{month:02d}"
        query_income = query_income.filter(models.Transaction.date.startswith(date_prefix))
        query_expenses = query_expenses.filter(models.Transaction.date.startswith(date_prefix))
        
    income = query_income.all()
    expenses = query_expenses.all()

    # Activities list combines income and expenses
    activities = []
    for transaction in income + expenses:
        activities.append({
            "date": transaction.date,
            "type": transaction.type,
            "amount": transaction.amount,
            "description": transaction.description,
            "category": transaction.category,
            "is_recurring": transaction.is_recurring,
            "goal_id": transaction.goal_id,
            "currency": transaction.currency
        })

    # Sort activities by date descending (simple string sort works for YYYY-MM-DD)
    activities.sort(key=lambda x: x["date"], reverse=True)

    return {
        "income": [{"amount": t.amount, "description": t.description, "date": t.date, "goal_id": t.goal_id, "category": t.category, "is_recurring": t.is_recurring, "currency": t.currency} for t in income],
        "expenses": [{"amount": t.amount, "description": t.description, "date": t.date, "goal_id": t.goal_id, "category": t.category, "is_recurring": t.is_recurring, "currency": t.currency} for t in expenses],
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
        date=transaction.date,
        category=transaction.category,
        is_recurring=transaction.is_recurring,
        goal_id=transaction.goal_id,
        currency=transaction.currency
    )
    db.add(db_transaction)

    # Update financial summary (only for TRY for now, or total balance? The summary seems to be in TRY)
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        summary = models.FinancialSummary(user_id=user_id)
        db.add(summary)

    # Note: Summary logic now accounts for currency conversion to TRY
    amount_in_try = convert_to_try(transaction.amount, transaction.currency)
    
    if transaction.type == "gelir":
        summary.monthly_income += amount_in_try
    elif transaction.type == "gider":
        summary.monthly_expense += amount_in_try

    summary.monthly_savings = summary.monthly_income - summary.monthly_expense

    db.commit()
    return {"message": "Transaction added successfully", "id": db_transaction.id}


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
@router.get("/goals", response_model=List[schemas.GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()
    return goals

@router.post("/goals", response_model=schemas.GoalResponse)
def create_goal(
    goal_create: schemas.GoalCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    new_goal = models.Goal(
        user_id=user_id,
        title=goal_create.title.strip(),
        target_amount=goal_create.target_amount,
        category=goal_create.category,
        color=goal_create.color,
        is_completed=goal_create.is_completed
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


@router.put("/goals/{goal_id}", response_model=schemas.GoalResponse)
def update_goal(
    goal_id: int,
    goal_update: schemas.GoalCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.title = goal_update.title.strip()
    goal.target_amount = goal_update.target_amount
    goal.category = goal_update.category
    goal.color = goal_update.color
    goal.is_completed = goal_update.is_completed

    db.commit()
    db.refresh(goal)
    return goal

@router.post("/goals/{goal_id}/purchase")
def purchase_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    if goal.is_completed:
        raise HTTPException(status_code=400, detail="Goal is already completed")

    # 1. Mark goal as completed
    goal.is_completed = True
    
    # 2. Add an explicit expense transaction for purchasing the target
    expense_txn = models.Transaction(
        user_id=user_id,
        amount=goal.target_amount,
        description=f"Satın Alma: {goal.title}",
        type="gider",
        category="Hedef",
        date=datetime.now().strftime("%Y-%m-%d"),
        goal_id=goal.id
    )
    db.add(expense_txn)
    
    # 3. Check if there's excess income over the goal target → save as TRY
    total_goal_income = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.goal_id == goal.id,
        models.Transaction.type == "gelir"
    ).all()
    total_saved = sum(convert_to_try(t.amount, t.currency) for t in total_goal_income)
    excess = total_saved - goal.target_amount
    if excess > 0:
        saving = models.Saving(
            user_id=user_id,
            amount=round(excess, 2),
            currency="TRY",
            description=f"Fazla Birikim: {goal.title}",
            date=datetime.now().strftime("%Y-%m-%d")
        )
        db.add(saving)
    
    # 4. Apply deduction to financial summary
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        summary = models.FinancialSummary(user_id=user_id)
        db.add(summary)
        
    summary.monthly_expense += goal.target_amount
    summary.monthly_savings = summary.monthly_income - summary.monthly_expense
    
    db.commit()
    return {"message": "Goal securely purchased", "goal": {"id": goal.id, "is_completed": goal.is_completed}}


class GoalFundRequest(schemas.BaseModel):
    saving_id: int

@router.post("/goals/{goal_id}/fund")
def fund_goal_from_saving(
    goal_id: int,
    req: GoalFundRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.is_completed:
        raise HTTPException(status_code=400, detail="Goal is already completed")

    saving = db.query(models.Saving).filter(models.Saving.id == req.saving_id, models.Saving.user_id == user_id).first()
    if not saving:
        raise HTTPException(status_code=404, detail="Saving not found")

    # Convert saving to TRY
    amount_try = convert_to_try(saving.amount, saving.currency)

    # Create income transaction tagged to goal
    txn = models.Transaction(
        user_id=user_id,
        amount=amount_try,
        description=f"Varlıktan Hedefe: {saving.description or saving.currency} → {goal.title}",
        type="gelir",
        category="Hedef",
        date=datetime.now().strftime("%Y-%m-%d"),
        goal_id=goal.id,
        currency="TRY"
    )
    db.add(txn)

    # Delete the saving
    db.delete(saving)
    db.commit()

    return {"message": f"Saving applied to goal '{goal.title}'", "amount_try": amount_try}

@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}



# User Profile Endpoints
@router.get("/user/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.commit()
    db.refresh(user)
    return {"name": user.name or "", "job_type": user.job_type, "monthly_salary": user.monthly_salary}


# Savings Endpoints
@router.get("/savings", response_model=List[schemas.SavingResponse])
def get_savings(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    savings = db.query(models.Saving).filter(models.Saving.user_id == user_id).all()
    return savings

@router.post("/savings", response_model=schemas.SavingResponse)
def add_saving(
    saving: schemas.SavingCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Upsert: if a saving with the same currency already exists, increment the balance
    existing = db.query(models.Saving).filter(
        models.Saving.user_id == user_id,
        models.Saving.currency == saving.currency
    ).first()

    if existing:
        existing.amount += saving.amount
        existing.date = saving.date
        if saving.description:
            existing.description = saving.description
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_saving = models.Saving(
            user_id=user_id,
            amount=saving.amount,
            currency=saving.currency,
            description=saving.description,
            date=saving.date
        )
        db.add(db_saving)
        db.commit()
        db.refresh(db_saving)
        return db_saving

@router.delete("/savings/{saving_id}")
def delete_saving(
    saving_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    saving = db.query(models.Saving).filter(models.Saving.id == saving_id, models.Saving.user_id == user_id).first()
    if not saving:
        raise HTTPException(status_code=404, detail="Saving not found")
    
    db.delete(saving)
    db.commit()
    return {"message": "Saving deleted successfully"}


@router.put("/user/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    profile: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = profile.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.commit()
    db.refresh(user)
    return {"name": user.name or "", "job_type": user.job_type, "monthly_salary": user.monthly_salary}


# Saved Expense Template Endpoints
@router.get("/saved-expenses", response_model=List[schemas.SavedExpenseResponse])
def get_saved_expenses(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return db.query(models.SavedExpense).filter(models.SavedExpense.user_id == user_id).all()

@router.post("/saved-expenses", response_model=schemas.SavedExpenseResponse)
def create_saved_expense(
    expense: schemas.SavedExpenseCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    db_expense = models.SavedExpense(
        user_id=user_id,
        label=expense.label.strip(),
        amount=expense.amount,
        category=expense.category
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/saved-expenses/{expense_id}")
def delete_saved_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    expense = db.query(models.SavedExpense).filter(
        models.SavedExpense.id == expense_id,
        models.SavedExpense.user_id == user_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Saved expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Saved expense deleted successfully"}

@router.post("/saved-expenses/{expense_id}/apply")
def apply_saved_expense(
    expense_id: int,
    apply_data: schemas.SavedExpenseApply = schemas.SavedExpenseApply(),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    expense = db.query(models.SavedExpense).filter(
        models.SavedExpense.id == expense_id,
        models.SavedExpense.user_id == user_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Saved expense not found")

    # Use override amount if provided, otherwise use template amount
    final_amount = apply_data.override_amount if apply_data.override_amount is not None else expense.amount

    # Create the gider transaction
    db_transaction = models.Transaction(
        user_id=user_id,
        amount=final_amount,
        description=expense.label,
        type="gider",
        date=datetime.now().strftime("%Y-%m-%d"),
        category=expense.category,
        is_recurring=False,
        currency="TRY"
    )
    db.add(db_transaction)

    # Update financial summary
    summary = db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    if not summary:
        summary = models.FinancialSummary(user_id=user_id)
        db.add(summary)
    summary.monthly_expense += final_amount
    summary.monthly_savings = summary.monthly_income - summary.monthly_expense

    db.commit()
    return {"message": f"Expense '{expense.label}' applied", "amount": final_amount, "id": db_transaction.id}