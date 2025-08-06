#schema.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ------------------ User Schemas ------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # 'öğretmen' veya 'veli'
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    username: str 
    password: str

class Token(BaseModel):
    access_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    first_name: str
    last_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ------------------ Student Schemas ------------------
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    sensitivities: Optional[str] = None
    interests: Optional[str] = None
    education_status: Optional[str] = None
    communication_level: Optional[str] = None
    user_id: int  

class StudentResponse(StudentCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ------------------ Test Schemas ------------------
class TestBase(BaseModel):
    test_title: str
    student_id: int

class TestCreate(TestBase):
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

class TestOut(TestBase):
    id: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ------------------ Result Schemas ------------------
class ResultBase(BaseModel):
    test_id: int
    student_id: int
    test_title: str
    ogrenci_adi: Optional[str] = None
    konu: Optional[str] = None
    dogru_cevap: Optional[int] = None
    yanlis_cevap: Optional[int] = None
    bos_cevap: Optional[int] = None
    toplam_soru: Optional[int] = None
    yuzde: Optional[float] = None
    sure: Optional[float] = None

class ResultCreate(ResultBase):
    pass

class ResultOut(ResultBase):
    id: int
    
    class Config:
        from_attributes = True

# ------------------ Report Schemas ------------------
class ReportBase(BaseModel):
    result_id: int
    rapor_metni: str

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: int
    
    class Config:
        from_attributes = True

# ------------------ Request Models ------------------
class CreateTestResultRequest(BaseModel):
    test_id: int
    student_id: int
    test_title: str
    ogrenci_adi: str
    konu: str
    dogru_cevap: int
    yanlis_cevap: int
    bos_cevap: int
    toplam_soru: int
    yuzde: float
    sure: float

class TextRequest(BaseModel):
    text: str

class StoryRequest(BaseModel):
    prompt: str

class TestGenerateRequest(BaseModel):
    test_type: str  # "math" veya "synonymAntonym"

