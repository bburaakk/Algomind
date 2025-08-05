# main.py

from fastapi import FastAPI, Depends, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from sqlalchemy import func, desc
from pydantic import BaseModel
from google.cloud import texttospeech
import tempfile
from fastapi.responses import FileResponse
import models, schema, database, jwt
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json

# --- Load environment and configure Gemini ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY bulunamadı. .env dosyasını kontrol edin.")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# --- DB setup ---
models.Base.metadata.create_all(bind=database.engine)

# --- FastAPI app ---
app = FastAPI()

# --- CORS (geliştirme için tüm domainlere izin, prod ortamda sınırla) ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---
class TextRequest(BaseModel):
    text: str

class StoryRequest(BaseModel):
    prompt: str

class TestGenerateRequest(BaseModel):
    test_type: str  # "math" veya "synonymAntonym"

# --- AUTH ---
@app.post("/signup")
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
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

# --- STUDENTS ---
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

# --- TESTS ---
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

# --- REPORTS ---
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

# --- ÖĞRENCİYE ÖZEL RAPORLAR ---
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

# --- GOOGLE CLOUD TTS ---
@app.post("/tts/")
async def tts_endpoint(request: TextRequest):
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="tr-TR",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(response.audio_content)
            tmp_filename = tmp_file.name
        return FileResponse(tmp_filename, media_type="audio/mpeg", filename="output.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- GEMINI STORY & TEST ENDPOINTS (SAME MODEL) ---

def gemini_generate(prompt: str, response_mime_type: str = "text/plain") -> str:
    """
    Gemini model ile içerik üretir.
    response_mime_type: "text/plain" veya "application/json"
    """
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={"response_mime_type": response_mime_type}
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {e}")

@app.post("/story/")
def generate_story(request: StoryRequest):
    story = gemini_generate(request.prompt, response_mime_type="text/plain")
    return {"story": story}

@app.post("/create_test")
def create_test_endpoint(request: TestGenerateRequest = Body(...)):
    if request.test_type == 'math':
        prompt = (
            "Bana 10 adet matematik sorusu oluştur. Sorular ilkokul seviyesinde olmalı ve toplama, çıkarma, çarpma ve bölme işlemlerini içermeli. "
            "Her soru için 2 seçenek ver. JSON formatında yanıt ver. "
            "Örnek: [ "
            '{"question": "25 + 23 = ?", "correct_answer": "48", "options": ["48", "47"]}, '
            '{"question": "12 - 4 = ?", "correct_answer": "8", "options": ["8", "9"]} ] '
            "- Toplama/çıkarma: 1-50 arası sayılar. "
            "- Çarpma/bölme: 1-50 arası sayılar, sonuçlar tam sayı olmalı. "
            "- Her soruda 2 farklı seçenek olmalı ve doğru cevap seçenekler arasında bulunmalı."
        )
    elif request.test_type == 'synonymAntonym':
        prompt = (
            "Bana 10 adet eş ve zıt anlamlı kelime sorusu oluştur. Sorular ilkokul seviyesinde olmalı ve temel kelimelerden oluşmalı. "
            "Soruların yarısı eş anlamlı, yarısı zıt anlamlı olmalı. Her soru için bir kelime, onun eş veya zıt anlamlısını içeren iki seçenek ver. "
            "JSON formatında yanıt ver. "
            "Örnek: ["
            '{"question": "\'Sıcak\' kelimesinin zıt anlamlısı nedir?", "correct_answer": "Soğuk", "options": ["Ilık", "Soğuk"]}, '
            '{"question": "\'Hürriyet\' kelimesinin eş anlamlısı nedir?", "correct_answer": "Özgürlük", "options": ["Tutsaklık", "Özgürlük"]} ]'
        )
    else:
        raise HTTPException(status_code=400, detail="Geçersiz test_type. 'math' veya 'synonymAntonym' olmalı.")

    # Gemini'den JSON bekleniyor
    raw_response = gemini_generate(prompt, response_mime_type="application/json")

    # Eğer cevap ```json ... ``` formatındaysa temizle
    json_string = raw_response.strip()
    if json_string.startswith("```json") and json_string.endswith("```"):
        json_string = json_string[7:-3].strip()

    try:
        questions = json.loads(json_string)
        if not (isinstance(questions, list) and all(isinstance(q, dict) for q in questions)):
            raise HTTPException(status_code=500, detail="API yanıtı beklenen formatta değil.")
        return {"questions": questions}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON ayrıştırma hatası: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genel hata: {e}")
#-------------------------------- Gemini Report --------------------
class CreateReportRequest(BaseModel):
    student_id: int
    test_id: int
    konu: str
    toplam_soru: int
    dogru_cevap: int
    yanlis_cevap: int
    bos_cevap: int
    yuzde: float
    sure: int
    ogrenci_adi: str

def generate_report_comment(report_data: dict) -> str:
    prompts = {
        "Hayvan Tanıma Testi": "Bu hayvan tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, hayvanlar hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Eş ve Zıt Anlamlı Kelimeler Testi": "Bu  testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, besinler hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Nesne Tanıma Testi": "Bu nesne tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, nesneler hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Yiyecekler Testi": "Bu yiyecek tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, sağlıklı beslenme farkındalığını ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Renk Tanıma Testi": "Bu renk tanıma testi sonuçlarına göre öğrencinin renkleri tanıma becerisini, görsel algısını ve dikkat süresini analiz et, gelişim alanlarını belirt ve önerilerde bulun.",
        "Matematik Testi": "Bu matematik testi sonuçlarına göre öğrencinin temel işlem becerilerini, problem çözme yeteneğini ve dikkat süresini analiz et, güçlü ve zayıf yönlerini belirt ve gelişim için önerilerde bulun."
    }

    base_prompt = f"""
Aşağıdaki öğrenci test sonuçlarına göre detaylı bir rapor ve yorum oluştur:
Öğrenci Adı: {report_data.get('ogrenci_adi', 'Bilinmiyor')}
Konu: {report_data.get('konu', 'Bilinmiyor')}
Toplam Soru: {report_data.get('toplam_soru', 0)}
Doğru Cevap: {report_data.get('dogru_cevap', 0)}
Yanlış Cevap: {report_data.get('yanlis_cevap', 0)}
Boş Cevap: {report_data.get('bos_cevap', 0)}
Başarı Yüzdesi: %{report_data.get('yuzde', 0.0)}
Test Süresi: {report_data.get('sure', 0)} saniye

Yorum İsteği: {prompts.get(report_data.get('konu'), "Lütfen öğrencinin performansını değerlendir.")}
Motivasyonunu artıracak pozitif bir dil kullan.
"""
    try:
        response = gemini_model.generate_content(base_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API hatası: {e}")
        return "Rapor yorumu alınırken bir hata oluştu."

@app.post("/create_report", response_model=schema.ReportOut)
def create_report_with_gemini(request: CreateReportRequest, db: Session = Depends(get_db)):
    try:
        report_data = request.dict()
        gemini_comment = generate_report_comment(report_data)
        db_report = models.Report(
            student_id=request.student_id,
            test_id=request.test_id,
            konu=request.konu,
            toplam_soru=request.toplam_soru,
            dogru_cevap=request.dogru_cevap,
            yanlis_cevap=request.yanlis_cevap,
            bos_cevap=request.bos_cevap,
            yuzde=request.yuzde,
            sure=request.sure,
            yorum=gemini_comment
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
