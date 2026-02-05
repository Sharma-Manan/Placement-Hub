from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field



class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    role: Literal["student", "coordinator"]

    first_name: str
    last_name: str

    roll_no: Optional[str] = None
    department: Optional[str] = None
    batch_year: Optional[int] = None
    cgpa: Optional[float] = None



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
