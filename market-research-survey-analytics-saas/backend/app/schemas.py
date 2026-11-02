from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2, max_length=255)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    full_name: str
    email: str

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str = ""
    research_objective: str = ""

class ProjectOut(ProjectCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class DatasetOut(BaseModel):
    id: int
    project_id: int
    original_filename: str
    row_count: int
    column_count: int
    uploaded_at: datetime
    class Config:
        from_attributes = True
