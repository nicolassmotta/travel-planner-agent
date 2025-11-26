from pydantic import BaseModel, field_validator
from typing import Optional

# --- Schemas de Autenticação ---
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Schemas de Viagem (Movido do main.py para cá) ---
class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: str
    returnDate: Optional[str] = None
    totalBudget: float
    nightlyBudget: float
    preferences: str

    @field_validator('totalBudget', 'nightlyBudget')
    def budgets_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('O orçamento não pode ser negativo')
        return v

class PlanDownloadRequest(BaseModel):
    plan: str