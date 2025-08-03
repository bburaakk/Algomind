# main.py

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from sqlalchemy import func, desc

import models, schema, database, jwt

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS ayarları
origins = ["*"]  # Gerekirse mobil uygulamanın IP adresiyle sınırlandırabilirsin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Veritabanı bağlantısı
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ AUTH ------------------

@app.post("/signup")
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) |
        (models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=schema.Token)
def login(user: schema.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"access_token": token}

@app.get("/user/me")
def read_users_me(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = jwt.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at
    }

# ------------------ STUDENTS ------------------

@app.post("/students", response_model=schema.StudentResponse)
def create_student(student: schema.StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students", response_model=List[schema.StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@app.get("/students/{student_id}", response_model=schema.StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# ------------------ TESTS ------------------

@app.post("/tests/", response_model=schema.TestOut)
def create_test(test: schema.TestCreate, db: Session = Depends(get_db)):
    db_test = models.Test(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@app.get("/tests/", response_model=List[schema.TestOut])
def get_tests(db: Session = Depends(get_db)):
    return db.query(models.Test).all()

# ------------------ REPORTS ------------------

@app.post("/reports/", response_model=schema.ReportOut)
def create_report(report: schema.ReportCreate, db: Session = Depends(get_db)):
    db_report = models.Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@app.get("/reports/", response_model=List[schema.ReportOut])
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(models.Report).all()

@app.get("/reports/by-student/{student_id}", response_model=List[schema.ReportOut])
def get_reports_by_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Report).filter(models.Report.student_id == student_id).all()

@app.get("/reports/by-test/{test_id}", response_model=List[schema.ReportOut])
def get_reports_by_test(test_id: int, db: Session = Depends(get_db)):
    return db.query(models.Report).filter(models.Report.test_id == test_id).all()

@app.get("/reports/latest", response_model=schema.ReportOut)
def get_latest_report(db: Session = Depends(get_db)):
    latest = db.query(models.Report).order_by(desc(models.Report.id)).first()
    if not latest:
        raise HTTPException(status_code=404, detail="Hiç rapor yok.")
    return latest

@app.get("/reports/summary")
def get_report_summary(db: Session = Depends(get_db)):
    return {
        "toplam_rapor": db.query(func.count(models.Report.id)).scalar() or 0,
        "ortalama_yuzde": round(db.query(func.avg(models.Report.yuzde)).scalar() or 0, 2),
        "ortalama_sure_saniye": round(db.query(func.avg(models.Report.sure)).scalar() or 0, 2),
        "toplam_dogru": db.query(func.sum(models.Report.dogru_cevap)).scalar() or 0,
        "toplam_yanlis": db.query(func.sum(models.Report.yanlis_cevap)).scalar() or 0,
        "toplam_bos": db.query(func.sum(models.Report.bos_cevap)).scalar() or 0,
    }

# ------------------ ÖĞRENCİYE ÖZEL RAPORLAR ------------------

@app.get("/students/{student_id}/reports-summary")
def student_report_summary(student_id: int, db: Session = Depends(get_db)):
    total_tests = db.query(func.count(models.Report.id)).filter(models.Report.student_id == student_id).scalar()
    avg_score = db.query(func.avg(models.Report.yuzde)).filter(models.Report.student_id == student_id).scalar()
    avg_time = db.query(func.avg(models.Report.sure)).filter(models.Report.student_id == student_id).scalar()
    total_correct = db.query(func.sum(models.Report.dogru_cevap)).filter(models.Report.student_id == student_id).scalar()
    total_wrong = db.query(func.sum(models.Report.yanlis_cevap)).filter(models.Report.student_id == student_id).scalar()

    return {
        "ogrenci_id": student_id,
        "cozulen_test_sayisi": total_tests or 0,
        "ortalama_basarim_yuzdesi": round(avg_score or 0, 2),
        "ortalama_sure_saniye": round(avg_time or 0, 2),
        "toplam_dogru": total_correct or 0,
        "toplam_yanlis": total_wrong or 0
    }

@app.get("/students/{student_id}/reports-detailed", response_model=List[schema.ReportOut])
def student_detailed_reports(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Report).filter(models.Report.student_id == student_id).order_by(desc(models.Report.id)).all()
