from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from algomind.data.api_config import API_KEY
import requests
import json
import google.generativeai as genai


genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def show_popup(title, message):
    """
    Ekranda bir bilgilendirme penceresi (popup) gösterir.

    Args:
        title (str): Pencerenin başlığı.
        message (str): Pencerede gösterilecek mesaj.
    """
    popup = Popup(title=title,
                  content=Label(text=message, halign='center'),
                  size_hint=(0.8, 0.3),
                  title_align='center')
    popup.open()


def clear_text_inputs(screen, fields):
    """
    Belirtilen ekrandaki metin giriş alanlarını temizler.

    Args:
        screen: Alanların bulunduğu ekran nesnesi.
        fields (list): Temizlenecek alanların id'lerinin listesi.
    """
    for field_id in fields:
        if hasattr(screen.ids, field_id):
            widget = screen.ids[field_id]
            if isinstance(widget, TextInput):
                widget.text = ""


def generate_test_questions(test_type):
    """
    Gemini API kullanarak belirtilen türde test soruları oluşturur.

    Args:
        test_type (str): 'math' veya 'synonymAntonym' gibi test türü.

    Returns:
        list: Soru ve cevapları içeren bir liste veya hata durumunda None.
    """
    if test_type == 'math':
        prompt = """
        Bana 10 adet matematik sorusu oluştur. Sorular ilkokul seviyesinde olmalı ve toplama, çıkarma, çarpma ve bölme işlemlerini içermeli. Her soru için 2 seçenek ver. JSON formatında yanıt ver.
        Örnek:
        [ 
            {"question": "25 + 23 = ?", "correct_answer": "48", "options": ["48", "47"]},
            {"question": "12 - 4 = ?", "correct_answer": "8", "options": ["8", "9"]}
        ]
        - Toplama/çıkarma: 1-50 arası sayılar.
        - Çarpma/bölme: 1-50 arası sayılar, sonuçlar tam sayı olmalı.
        - Her soruda 2 farklı seçenek olmalı ve doğru cevap seçenekler arasında bulunmalı.
        """
    elif test_type == 'synonymAntonym':
        prompt = """
                Bana 10 adet eş ve zıt anlamlı kelime sorusu oluştur. Sorular ilkokul seviyesinde olmalı ve temel kelimelerden oluşmalı. Soruların yarısı eş anlamlı, yarısı zıt anlamlı olmalı. Her soru için bir kelime, onun eş veya zıt anlamlısını içeren iki seçenek ver. JSON formatında yanıt ver. Örnek:
                [
                    {"question": "'Sıcak' kelimesinin zıt anlamlısı nedir?", "correct_answer": "Soğuk", "options": ["Ilık", "Soğuk"]},
                    {"question": "'Hürriyet' kelimesinin eş anlamlısı nedir?", "correct_answer": "Özgürlük", "options": ["Tutsaklık", "Özgürlük"]}
                ]
                """
    else:
        return None

    chatHistory = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": chatHistory, "generationConfig": {"responseMimeType": "application/json"}}
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    try:
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        json_string = result['candidates'][0]['content']['parts'][0]['text']
        
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[7:-3].strip()
            
        questions = json.loads(json_string)
        
        if isinstance(questions, list) and all(isinstance(q, dict) for q in questions):
            print(f"API'den {test_type} soruları başarıyla çekildi.")
            return questions
        else:
            print(f"API'den beklenen formatta ({test_type}) yanıt alınamadı.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında bir ağ hatası oluştu: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"API yanıtı JSON olarak ayrıştırılamadı: {e}")
        return None
    except Exception as e:
        print(f"Genel bir hata oluştu: {e}")
        return None


def generate_report_comment(report_data):
    """
    Gemini API kullanarak test sonuçları için bir uzman yorumu oluşturur.

    Args:
        report_data (dict): Rapor verilerini içeren sözlük.

    Returns:
        str: Oluşturulan yorum veya hata durumunda bir hata mesajı.
    """
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
        chatHistory = [{"role": "user", "parts": [{"text": base_prompt}]}]
        payload = {"contents": chatHistory}
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        gemini_comment = result['candidates'][0]['content']['parts'][0]['text']
        return gemini_comment
    except Exception as e:
        print(f"Gemini API hatası: {e}")
        return "Rapor yorumu alınırken bir hata oluştu."


