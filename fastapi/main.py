# main.py

from fastapi import FastAPI, Depends, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from sqlalchemy import func, desc
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

@app.get("/tests/{test_id}", response_model=schema.TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

# --- RESULTS ---
@app.get("/results/", response_model=List[schema.ResultOut])
def get_all_results(db: Session = Depends(get_db)):
    return db.query(models.Result).all()

@app.get("/results/by-student/{student_id}", response_model=List[schema.ResultOut])
def get_results_by_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Result).filter(models.Result.student_id == student_id).all()

@app.get("/results/by-test/{test_id}", response_model=List[schema.ResultOut])
def get_results_by_test(test_id: int, db: Session = Depends(get_db)):
    return db.query(models.Result).filter(models.Result.test_id == test_id).all()

@app.get("/results/latest", response_model=schema.ResultOut)
def get_latest_result(db: Session = Depends(get_db)):
    latest = db.query(models.Result).order_by(desc(models.Result.id)).first()
    if not latest:
        raise HTTPException(status_code=404, detail="Hiç sonuç yok.")
    return latest

@app.get("/results/summary")
def get_results_summary(db: Session = Depends(get_db)):
    return {
        "toplam_sonuc": db.query(func.count(models.Result.id)).scalar() or 0,
        "ortalama_yuzde": round(db.query(func.avg(models.Result.yuzde)).scalar() or 0, 2),
        "ortalama_sure_saniye": round(db.query(func.avg(models.Result.sure)).scalar() or 0, 2),
        "toplam_dogru": db.query(func.sum(models.Result.dogru_cevap)).scalar() or 0,
        "toplam_yanlis": db.query(func.sum(models.Result.yanlis_cevap)).scalar() or 0,
        "toplam_bos": db.query(func.sum(models.Result.bos_cevap)).scalar() or 0,
    }

# --- REPORTS ---
@app.get("/reports/", response_model=List[schema.ReportOut])
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(models.Report).all()

@app.get("/reports/by-result/{result_id}", response_model=schema.ReportOut)
def get_report_by_result(result_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.result_id == result_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Bu sonuç için rapor bulunamadı.")
    return report

@app.get("/reports/latest", response_model=schema.ReportOut)
def get_latest_report(db: Session = Depends(get_db)):
    latest = db.query(models.Report).order_by(desc(models.Report.id)).first()
    if not latest:
        raise HTTPException(status_code=404, detail="Hiç rapor yok.")
    return latest

# --- ÖĞRENCİYE ÖZEL SONUÇLAR ---
@app.get("/students/{student_id}/results-summary")
def student_results_summary(student_id: int, db: Session = Depends(get_db)):
    total_tests = db.query(func.count(models.Result.id)).filter(models.Result.student_id == student_id).scalar()
    avg_score = db.query(func.avg(models.Result.yuzde)).filter(models.Result.student_id == student_id).scalar()
    avg_time = db.query(func.avg(models.Result.sure)).filter(models.Result.student_id == student_id).scalar()
    total_correct = db.query(func.sum(models.Result.dogru_cevap)).filter(models.Result.student_id == student_id).scalar()
    total_wrong = db.query(func.sum(models.Result.yanlis_cevap)).filter(models.Result.student_id == student_id).scalar()
    return {
        "ogrenci_id": student_id,
        "cozulen_test_sayisi": total_tests or 0,
        "ortalama_basarim_yuzdesi": round(avg_score or 0, 2),
        "ortalama_sure_saniye": round(avg_time or 0, 2),
        "toplam_dogru": total_correct or 0,
        "toplam_yanlis": total_wrong or 0
    }

@app.get("/students/{student_id}/results-detailed", response_model=List[schema.ResultOut])
def student_detailed_results(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Result).filter(models.Result.student_id == student_id).order_by(desc(models.Result.id)).all()

# --- GOOGLE CLOUD TTS ---
@app.post("/tts/")
async def tts_endpoint(request: schema.TextRequest):
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

# --- GEMINI STORY & TEST ENDPOINTS ---

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
def generate_story(request: schema.StoryRequest):
    story = gemini_generate(request.prompt, response_mime_type="text/plain")
    return {"story": story}

@app.post("/create_test")
def create_test_endpoint(request: schema.TestGenerateRequest = Body(...)):
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

# --- GEMINI REPORT GENERATION ---

def generate_report_comment(report_data: dict) -> str:
    """
    Gemini ile öğrencinin test sonuçlarına göre rapor oluşturur
    """
    prompts = {
        "Hayvan Tanıma Testi": "Bu hayvan tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, hayvanlar hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Eş ve Zıt Anlamlı Kelimeler Testi": "Bu eş ve zıt anlamlı kelimeler testi sonuçlarına göre öğrencinin kelime haznesini, kavrama becerisini, dil gelişimini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
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
Motivasyonunu artıracak pozitif bir dil kullan ve yapıcı öneriler sun.
"""
    try:
        response = gemini_model.generate_content(base_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API hatası: {e}")
        return "Rapor yorumu alınırken bir hata oluştu."

@app.post("/create_test_result_and_report")
def create_test_result_and_report(request: schema.CreateTestResultRequest, db: Session = Depends(get_db)):
    """
    Test sonucunu kaydeder ve Gemini ile rapor oluşturur
    """
    try:
        # 1. results tablosuna kayıt
        new_result = models.Result(
            test_id=request.test_id,
            student_id=request.student_id,
            test_title=request.test_title,
            ogrenci_adi=request.ogrenci_adi,
            konu=request.konu,
            dogru_cevap=request.dogru_cevap,
            yanlis_cevap=request.yanlis_cevap,
            bos_cevap=request.bos_cevap,
            toplam_soru=request.toplam_soru,
            yuzde=request.yuzde,
            sure=request.sure
        )
        db.add(new_result)
        db.commit()
        db.refresh(new_result)

        # 2. Gemini ile rapor oluştur
        gemini_prompt_data = request.dict()
        gemini_comment = generate_report_comment(gemini_prompt_data)

        # 3. report tablosuna kayıt
        new_report = models.Report(
            result_id=new_result.id,
            rapor_metni=gemini_comment
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return {
            "result_id": new_result.id,
            "report_id": new_report.id,
            "rapor_metni": gemini_comment,
            "message": "Test sonucu ve rapor başarıyla kaydedildi."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Hata oluştu: {str(e)}")
