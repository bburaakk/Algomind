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
    total_correct = db.query(func.sum(models.Result.dogru_cevap)).filter(
        models.Result.student_id == student_id).scalar()
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
            "- Ve testler hep farklı olsun, aynı testleri verme"
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


# --- IMPROVED STUDENT INFO RETRIEVAL ---

def get_student_info_for_report(db: Session, student_id: int) -> dict:
    """
    Öğrencinin hassasiyetleri, ilgi alanları ve diğer bilgilerini veritabanından alır
    Geliştirilmiş hata yönetimi ve veri doğrulama ile
    """
    try:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if not student:
            print(f"Uyarı: {student_id} ID'li öğrenci bulunamadı.")
            return {}

        # Boş değerleri kontrol et ve temizle
        student_info = {
            "id": student.id,
            "first_name": student.first_name or "",
            "last_name": student.last_name or "",
            "age": student.age,
            "sensitivities": student.sensitivities.strip() if student.sensitivities else None,
            "interests": student.interests.strip() if student.interests else None,
            "communication_level": student.communication_level.strip() if student.communication_level else None,
            "education_status": student.education_status.strip() if student.education_status else None
        }

        # Debug için öğrenci bilgilerini logla
        print(f"Öğrenci bilgileri alındı - ID: {student_id}")
        print(f"- Hassasiyetler: {'Var' if student_info['sensitivities'] else 'Yok'}")
        print(f"- İlgi alanları: {'Var' if student_info['interests'] else 'Yok'}")
        print(f"- İletişim düzeyi: {'Var' if student_info['communication_level'] else 'Yok'}")
        print(f"- Eğitim durumu: {'Var' if student_info['education_status'] else 'Yok'}")

        return student_info

    except Exception as e:
        print(f"Öğrenci bilgileri alınırken hata: {e}")
        return {}


# --- ENHANCED REPORT GENERATION ---

def generate_report_comment(report_data: dict, student_info: dict = None) -> str:
    """
    Gemini ile öğrencinin test sonuçlarına göre kişiselleştirilmiş rapor oluşturur
    Geliştirilmiş öğrenci bilgilerini kullanır
    """
    prompts = {
        "Hayvan Tanıma Testi": "Bu hayvan tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, hayvanlar hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Eş ve Zıt Anlamlı Kelimeler Testi": "Bu eş ve zıt anlamlı kelimeler testi sonuçlarına göre öğrencinin kelime haznesini, kavrama becerisini, dil gelişimini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Nesne Tanıma Testi": "Bu nesne tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, nesneler hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Yiyecekler Testi": "Bu yiyecek tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, sağlıklı beslenme farkındalığını ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
        "Renk Tanıma Testi": "Bu renk tanıma testi sonuçlarına göre öğrencinin renkleri tanıma becerisini, görsel algısını ve dikkat süresini analiz et, gelişim alanlarını belirt ve önerilerde bulun.",
        "Matematik Testi": "Bu matematik testi sonuçlarına göre öğrencinin temel işlem becerilerini, problem çözme yeteneğini ve dikkat süresini analiz et, güçlü ve zayıf yönlerini belirt ve gelişim için önerilerde bulun."
    }

    # Test türüne göre uygun prompt'u seç
    test_type = report_data.get('konu', 'Genel Test')
    specific_prompt = prompts.get(test_type,
                                  "Bu test sonuçlarına göre öğrencinin performansını analiz et ve gelişim önerileri sun.")

    # Geliştirilmiş öğrenci bilgilerini hazırla
    student_context = ""
    personal_info_available = False

    if student_info and isinstance(student_info, dict):
        # Temel bilgiler
        if student_info.get('age'):
            student_context += f"\n\nÖğrenci Yaşı: {student_info['age']}"

        # Hassasiyetler
        if student_info.get('sensitivities'):
            student_context += f"\n\nÖğrencinin Hassasiyetleri: {student_info['sensitivities']}"
            personal_info_available = True

        # İlgi alanları
        if student_info.get('interests'):
            student_context += f"\nÖğrencinin İlgi Alanları: {student_info['interests']}"
            personal_info_available = True

        # İletişim düzeyi
        if student_info.get('communication_level'):
            student_context += f"\nİletişim Düzeyi: {student_info['communication_level']}"
            personal_info_available = True

        # Eğitim durumu
        if student_info.get('education_status'):
            student_context += f"\nEğitim Durumu: {student_info['education_status']}"
            personal_info_available = True

    # Kişiselleştirme talimatı
    personalization_instruction = ""
    if personal_info_available:
        personalization_instruction = """

ÖNEMLİ: Yukarıda verilen öğrenci bilgilerini (hassasiyetler, ilgi alanları, iletişim düzeyi, eğitim durumu) mutlaka dikkate alarak önerilerinizi kişiselleştirin. Bu bilgileri öğrencinin bireysel ihtiyaçlarına göre somut önerilere dönüştürün."""
    else:
        student_context += "\n\nNot: Bu öğrenci için ek kişisel bilgi (hassasiyetler, ilgi alanları) henüz kaydedilmemiş."

    base_prompt = f"""Sen, otizm spektrumundaki çocukların gelişimine ve eğitimine odaklanan bir uzmansın. Aşağıdaki öğrenci test sonuçlarını kullanarak, eğitimciler için yol gösterici, olumlu bir dille yazılmış, kişiselleştirilmiş bir gelişim raporu oluştur.

{specific_prompt}

Öğrenci Test Sonuçları:
- Öğrenci Adı: {report_data.get('ogrenci_adi', 'Bilinmiyor')}
- Test Konusu: {report_data.get('konu', 'Bilinmiyor')}
- Toplam Soru: {report_data.get('toplam_soru', 0)}
- Doğru Cevap: {report_data.get('dogru_cevap', 0)}
- Yanlış Cevap: {report_data.get('yanlis_cevap', 0)}
- Boş Cevap: {report_data.get('bos_cevap', 0)}
- Başarı Yüzdesi: %{report_data.get('yuzde', 0.0)}
- Test Süresi: {report_data.get('sure', 0)} saniye

{student_context}{personalization_instruction}

Raporunuzu şu yapıda hazırlayın:

**Öğrenci Performans Raporu**

1. **Güçlü Yönleri:** Öğrencinin başarılı olduğu alanları ve testteki performansı hakkında olumlu gözlemler sun.

2. **Geliştirilmesi Gereken Alanlar:** Test sonuçlarına dayanarak, öğrencinin desteklenmesi gereken becerileri veya konu başlıklarını nazik bir dille belirt.

3. **Kişiselleştirilmiş Öneriler:** {"Öğrencinin hassasiyetleri ve ilgi alanlarını dikkate alarak" if personal_info_available else "Test sonuçlarına dayanarak"}, evde veya okulda uygulanabilecek somut ve pratik önerilerde bulun. {"Özellikle:" if personal_info_available else ""}
   {f"- İlgi alanlarını öğrenme sürecine nasıl dahil edebileceklerini" if personal_info_available else "- Öğrencinin ilgi çekici bulabileceği aktiviteleri"}
   {f"- Duyusal hassasiyetleri için nasıl bir ortam yaratılabileceğini" if personal_info_available else "- Rahat bir öğrenme ortamı yaratma yöntemlerini"}
   {f"- İletişim düzeyine uygun aktiviteleri" if personal_info_available else "- Etkili iletişim stratejilerini"}
   {f"- Eğitim durumuna uygun destekleme yöntemlerini açıkla" if personal_info_available else "- Öğrenmeyi destekleyici yöntemleri açıkla"}

4. **Genel Değerlendirme:** Raporu, çocuğun bireysel hızında ve kendi potansiyeliyle gelişimine odaklanan, motive edici bir kapanış cümlesiyle bitir.

Not: Raporunuz destekleyici, yapıcı ve umut verici bir tonda olmalıdır."""

    try:
        response = gemini_model.generate_content(base_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API hatası: {e}")
        return "Rapor yorumu alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin."


# --- ENHANCED CREATE TEST RESULT AND REPORT ---

@app.post("/create_test_result_and_report")
def create_test_result_and_report(request: schema.CreateTestResultRequest, db: Session = Depends(get_db)):
    """
    Test sonucunu kaydeder ve Gemini ile geliştirilmiş kişiselleştirilmiş rapor oluşturur
    """
    try:
        # 1. Önce öğrencinin var olup olmadığını kontrol et
        student = db.query(models.Student).filter(models.Student.id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"ID {request.student_id} olan öğrenci bulunamadı.")

        # 2. results tablosuna kayıt
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

        # 3. Öğrenci bilgilerini detaylı olarak al
        student_info = get_student_info_for_report(db, request.student_id)

        # 4. Gemini ile geliştirilmiş kişiselleştirilmiş rapor oluştur
        gemini_prompt_data = request.dict()
        gemini_comment = generate_report_comment(gemini_prompt_data, student_info)

        # 5. report tablosuna kayıt
        new_report = models.Report(
            result_id=new_result.id,
            rapor_metni=gemini_comment
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # 6. Kullanılan öğrenci bilgilerini özetle
        used_student_info = {
            "student_found": True,
            "student_name": f"{student_info.get('first_name', '')} {student_info.get('last_name', '')}".strip(),
            "age": student_info.get('age'),
            "has_sensitivities": bool(student_info.get('sensitivities')),
            "has_interests": bool(student_info.get('interests')),
            "has_communication_level": bool(student_info.get('communication_level')),
            "has_education_status": bool(student_info.get('education_status')),
            "personalization_level": "high" if any([
                student_info.get('sensitivities'),
                student_info.get('interests'),
                student_info.get('communication_level'),
                student_info.get('education_status')
            ]) else "basic"
        }

        return {
            "result_id": new_result.id,
            "report_id": new_report.id,
            "rapor_metni": gemini_comment,
            "message": "Test sonucu ve kişiselleştirilmiş rapor başarıyla kaydedildi.",
            "student_info_used": used_student_info
        }
    except Exception as e:
        db.rollback()
        print(f"Test sonucu ve rapor oluştururken hata: {e}")
        raise HTTPException(status_code=500, detail=f"Hata oluştu: {str(e)}")