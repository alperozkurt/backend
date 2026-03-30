from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]

    class Config:
        from_attributes = True  # for SQLAlchemy ORM (Pydantic v2)

class TransactionBase(BaseModel):
    amount: float
    description: str
    type: str  # 'gelir' or 'gider'
    date: str
    goal_id: Optional[int] = None
    category: str = "Genel"
    is_recurring: bool = False
    currency: str = "TRY"

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class FinancialSummaryResponse(BaseModel):
    month: str
    monthly_income: float
    monthly_expense: float
    monthly_savings: float

class FinancialSummaryUpdate(BaseModel):
    month: Optional[str] = None
    monthly_income: Optional[float] = None
    monthly_expense: Optional[float] = None
    monthly_savings: Optional[float] = None

class InvestmentProfileBase(BaseModel):
    profile: str  # 'korumacı', 'dengeli', 'agresif'

class InvestmentProfileCreate(InvestmentProfileBase):
    pass

class InvestmentProfileResponse(InvestmentProfileBase):
    id: int

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    name: str
    job_type: Optional[str] = None
    monthly_salary: Optional[float] = None

class UserProfileUpdate(BaseModel):
    name: str
    job_type: Optional[str] = None
    monthly_salary: Optional[float] = None

class GoalBase(BaseModel):
    title: str
    target_amount: float
    category: str = "Genel"
    color: str
    icon: str = "stars_rounded"
    is_completed: bool = False
    completed_at: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalResponse(GoalBase):
    id: int
    user_id: int
    saved_amount: float = 0.0

    class Config:
        from_attributes = True

class SavingBase(BaseModel):
    amount: float
    currency: str  # 'TRY', 'USD', 'EUR', 'GOLD'
    description: Optional[str] = None
    date: str

class SavingCreate(SavingBase):
    pass

class SavingResponse(SavingBase):
    id: int
    user_id: int
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class SavedExpenseBase(BaseModel):
    label: str
    amount: float
    category: str = "Genel"

class SavedExpenseCreate(SavedExpenseBase):
    pass

class SavedExpenseResponse(SavedExpenseBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class SavedExpenseApply(BaseModel):
    override_amount: Optional[float] = None