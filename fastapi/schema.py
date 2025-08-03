from pydantic import BaseModel, EmailStr
from typing import Optional

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

    class Config:
        from_attributes = True
# ------------------ Test ------------------

class TestBase(BaseModel):
    test_title: str
    student_id: int

class TestCreate(TestBase):
    pass

class TestOut(TestBase):
    id: int
    class Config:
        from_attributes = True             


# ------------------ Report ------------------
class ReportBase(BaseModel):
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

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: int
    class Config:
        from_attributes = True       
