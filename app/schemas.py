from pydantic import BaseModel, EmailStr
from typing import Optional

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

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int

    class Config:
        from_attributes = True

class FinancialSummaryResponse(BaseModel):
    monthly_income: float
    monthly_expense: float
    monthly_savings: float

class FinancialSummaryUpdate(BaseModel):
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

class UserProfileUpdate(BaseModel):
    name: str