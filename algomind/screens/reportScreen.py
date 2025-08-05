# reportScreen.py

from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from PyPDF2 import PdfReader
import threading
import os
import requests
import json

from algomind.helpers import generate_report_comment, show_popup
from algomind.data.api_config import API_KEY

class RaporEkrani(MDScreen):
    """
    Test sonuçlarını ve Gemini analizini gösteren ekran.
    """
    student_name_text = StringProperty("Öğrenci Yükleniyor...")

    def on_enter(self, *args):
        """
        Ekran görüntülendiğinde rapor verilerini yükler.
        """
        # Veri yüklemesini küçük bir gecikmeyle planla
        Clock.schedule_once(self.load_report_data, 0.1)
        super().on_enter(*args)

    def load_report_data(self, dt):
        """
        Gecikmeli olarak rapor verilerini yükler ve UI'ı günceller.
        """
        app = MDApp.get_running_app()
        report_data = getattr(app, 'last_test_result', None)

        if not report_data:
            show_popup("Hata", "Görüntülenecek rapor verisi bulunamadı.")
            if self.ids.report_content:
                self.ids.report_content.text = "Rapor verisi yok."
            self.student_name_text = "Öğrenci Raporu"
            return

        self.student_name_text = f"{report_data.get('ogrenci_adi', 'Bilinmiyor')} Raporu"
        
        # Rapor içeriğini ve Gemini yorumunu yükle
        self.fetch_and_display_report(report_data)

    def fetch_and_display_report(self, report_data):
        """
        Rapor verilerini formatlar ve Gemini'den yorum almak için bir thread başlatır.
        """
        # Önce temel istatistikleri göster
        initial_report_text = f"""
[b]Öğrenci:[/b] {report_data.get('ogrenci_adi', 'Bilinmiyor')}
[b]Konu:[/b] {report_data.get('konu', 'Bilinmiyor')}
[b]Toplam Soru:[/b] {report_data.get('toplam_soru', 0)}
[b]Doğru:[/b] {report_data.get('dogru_cevap', 0)}
[b]Yanlış:[/b] {report_data.get('yanlis_cevap', 0)}
[b]Başarı Yüzdesi:[/b] %{report_data.get('yuzde', 0.0)}
[b]Süre:[/b] {report_data.get('sure', 0)} saniye

[b]Gemini Yorumu:[/b]
[i]Yorum oluşturuluyor, lütfen bekleyin...[/i]
"""
        if self.ids.report_content:
            self.ids.report_content.text = initial_report_text.strip()

        # Gemini'den yorumu arkaplanda al
        threading.Thread(target=self._fetch_gemini_comment_thread, args=(report_data,)).start()

    def _read_pdf_criteria(self, file_path):
        """
        PDF dosyasının içeriğini metin olarak okur ve döndürür.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(current_dir))
            full_path = os.path.join(app_root_dir, file_path)
            print(f"Kontrol edilen PDF yolu: {full_path}")

            reader = PdfReader(full_path)
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() or ""
            return text_content
        except FileNotFoundError:
            print(f"Hata: {file_path} dosyası bulunamadı.")
            return "PDF dosyası okunamadı."
        except Exception as e:
            print(f"PDF okuma hatası: {e}")
            return "PDF okuma hatası."

    def _fetch_gemini_comment_thread(self, report_data):
        """
        requests kütüphanesini kullanarak Gemini'den rapor yorumu alır.
        """
        kriterler_metni = self._read_pdf_criteria("kriterler.pdf")
        standartlar_metni = self._read_pdf_criteria("raporlama_standartlari.pdf")

        base_prompt = f"""
        Aşağıdaki öğrenci test sonuçlarını ve ardından verilen değerlendirme kriterlerini ve raporlama standartlarını incele. Bu bilgilere göre öğrencinin performansını detaylı bir şekilde değerlendir ve rapor oluştur.

        [b]Değerlendirme Kriterleri:[/b]
        {kriterler_metni}

        [b]Raporlama Standartları:[/b]
        {standartlar_metni}

        [b]Öğrenci Test Sonuçları:[/b]
        Öğrenci Adı: {report_data['ogrenci_adi']}
        Konu: {report_data['konu']}
        Toplam Soru: {report_data['toplam_soru']}
        Doğru Cevap: {report_data['dogru_cevap']}
        Yanlış Cevap: {report_data['yanlis_cevap']}
        Boş Cevap: {report_data['bos_cevap']}
        Başarı Yüzdesi: %{report_data['yuzde']}
        Test Süresi: {report_data['sure']} saniye

        Motivasyonunu artıracak pozitif bir dil kullan.
        """

        try:
            chatHistory = [{"role": "user", "parts": [{"text": base_prompt}]}]
            payload = {"contents": chatHistory}
            apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            gemini_comment = result['candidates'][0]['content']['parts'][0]['text']

            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, gemini_comment))

        except requests.exceptions.RequestException as e:
            print(f"Gemini API'ye bağlanırken bir hata oluştu: {e}")
            Clock.schedule_once(
                lambda dt: self._update_report_ui(report_data, "Rapor yorumu alınırken bir bağlantı hatası oluştu."), 0)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Gemini yanıtını işlerken bir hata oluştu: {e}")
            print(f"API yanıtı: {response.text}")
            Clock.schedule_once(
                lambda dt: self._update_report_ui(report_data, "Rapor yorumu işlenirken bir hata oluştu."), 0)
        except Exception as e:
            print(f"Beklenmedik bir hata oluştu: {e}")
            Clock.schedule_once(
                lambda dt: self._update_report_ui(report_data, "Rapor yorumu alınırken bilinmeyen bir hata oluştu."), 0)

    def _update_report_ui(self, report_data, gemini_comment):
        """
        Gemini'den gelen yorumla rapor metnini günceller.
        """
        full_report_text = f"""
[b]Öğrenci:[/b] {report_data.get('ogrenci_adi', 'Bilinmiyor')}
[b]Konu:[/b] {report_data.get('konu', 'Bilinmiyor')}
[b]Toplam Soru:[/b] {report_data.get('toplam_soru', 0)}
[b]Doğru:[/b] {report_data.get('dogru_cevap', 0)}
[b]Yanlış:[/b] {report_data.get('yanlis_cevap', 0)}
[b]Başarı Yüzdesi:[/b] %{report_data.get('yuzde', 0.0)}
[b]Süre:[/b] {report_data.get('sure', 0)} saniye

[b]Gemini Yorumu:[/b]
{gemini_comment}
"""
        if self.ids.report_content:
            self.ids.report_content.text = full_report_text.strip()
