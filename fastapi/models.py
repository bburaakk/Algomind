from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(role.in_(["öğretmen", "veli"]), name="check_valid_role"),
    )
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    sensitivities = Column(Text)
    interests = Column(Text)
    education_status = Column(Text)
    communication_level = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    tests = relationship("Test", back_populates="student", cascade="all, delete")
    reports = relationship("Report", back_populates="student", cascade="all, delete")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    test_title = Column(String(255), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)

    student = relationship("Student", back_populates="tests")
    reports = relationship("Report", back_populates="test", cascade="all, delete")

   class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    test_title = Column(String)
    ogrenci_adi = Column(Text)
    konu = Column(Text)
    dogru_cevap = Column(Integer)
    yanlis_cevap = Column(Integer)
    bos_cevap = Column(Integer)
    toplam_soru = Column(Integer)
    yuzde = Column(Float)
    sure = Column(Float)

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("results.id", ondelete="CASCADE"))
    rapor_metni = Column(Text)
