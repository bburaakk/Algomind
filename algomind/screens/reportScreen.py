from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.app import MDApp
import threading
import requests
import json

from algomind.helpers import show_popup
from algomind.data.api_config import API_BASE_URL  # Backend URL'ini config'den al

class RaporEkrani(MDScreen):
    """
    Test sonuçlarını ve backend'den alınan rapor analizini gösteren ekran.
    """
    student_name_text = StringProperty("Öğrenci Yükleniyor...")

    def on_enter(self, *args):
        Clock.schedule_once(self.load_report_data, 0.1)
        super().on_enter(*args)

    def load_report_data(self, dt):
        """Rapor verilerini yükler ve gösterir"""
        app = MDApp.get_running_app()
        report_data = getattr(app, 'last_test_result', None)

        if not report_data:
            show_popup("Hata", "Görüntülenecek rapor verisi bulunamadı.")
            if self.ids.report_content:
                self.ids.report_content.text = "Rapor verisi yok."
            self.student_name_text = "Öğrenci Raporu"
            return

        self.student_name_text = f"{report_data.get('ogrenci_adi', 'Bilinmiyor')} Raporu"
        self.display_initial_report_and_fetch_analysis(report_data)

    def display_initial_report_and_fetch_analysis(self, report_data):
        """İlk rapor bilgilerini gösterir ve arka planda analiz getirir"""
        initial_report_text = f"""
[b]Öğrenci:[/b] {report_data.get('ogrenci_adi', 'Bilinmiyor')}
[b]Konu:[/b] {report_data.get('konu', 'Bilinmiyor')}
[b]Toplam Soru:[/b] {report_data.get('toplam_soru', 0)}
[b]Doğru:[/b] {report_data.get('dogru_cevap', 0)}
[b]Yanlış:[/b] {report_data.get('yanlis_cevap', 0)}
[b]Boş:[/b] {report_data.get('bos_cevap', 0)}
[b]Başarı Yüzdesi:[/b] %{report_data.get('yuzde', 0.0)}
[b]Süre:[/b] {report_data.get('sure', 0)} saniye

[b]Detaylı Analiz:[/b]
[i]Analiz oluşturuluyor, lütfen bekleyin...[/i]
"""
        if self.ids.report_content:
            self.ids.report_content.text = initial_report_text.strip()

        # Arka planda rapor analizi getir
        threading.Thread(target=self._fetch_report_analysis_thread, args=(report_data,)).start()

    def _fetch_report_analysis_thread(self, report_data):
        """Backend'den rapor analizi getirir"""
        try:
            # Option 1: Eğer result_id mevcutsa, mevcut raporu getir
            result_id = report_data.get('result_id')
            if result_id:
                report_text = self._get_existing_report(result_id)
                if report_text:
                    Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
                    return

            # Option 2: Yeni rapor oluştur
            report_text = self._create_new_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))

        except requests.exceptions.ConnectionError as e:
            print(f"Backend'e bağlanırken bağlantı hatası: {e}")
            error_msg = "Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin."
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, error_msg))
        
        except requests.exceptions.Timeout as e:
            print(f"Backend timeout hatası: {e}")
            error_msg = "Sunucu yanıt vermedi. Lütfen tekrar deneyin."
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, error_msg))
        
        except requests.exceptions.HTTPError as e:
            print(f"Backend HTTP hatası: {e}")
            if e.response.status_code == 404:
                error_msg = "Rapor bulunamadı."
            elif e.response.status_code == 500:
                error_msg = "Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin."
            else:
                error_msg = f"HTTP {e.response.status_code} hatası oluştu."
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, error_msg))
        
        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {e}")
            error_msg = "Sunucu yanıtı işlenemedi."
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, error_msg))
        
        except Exception as e:
            print(f"Beklenmedik hata: {e}")
            error_msg = "Rapor analizi alınırken bilinmeyen bir hata oluştu."
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, error_msg))

    def _get_existing_report(self, result_id):
        """Mevcut raporu backend'den getirir"""
        try:
            url = f"{API_BASE_URL}/reports/by-result/{result_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            report_data = response.json()
            return report_data.get('rapor_metni', 'Rapor metni bulunamadı.')
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Result ID {result_id} için rapor bulunamadı.")
                return None
            raise
        except Exception as e:
            print(f"Mevcut rapor alınırken hata: {e}")
            raise

    def _create_new_report(self, report_data):
        """Backend'de yeni rapor oluşturur"""
        try:
            # Test sonucu ve rapor oluştur
            url = f"{API_BASE_URL}/create_test_result_and_report"
            
            payload = {
                "test_id": report_data.get('test_id', 1),
                "student_id": report_data.get('student_id', 1),
                "test_title": report_data.get('test_title', report_data.get('konu', 'Test')),
                "ogrenci_adi": report_data.get('ogrenci_adi', 'Bilinmiyor'),
                "konu": report_data.get('konu', 'Bilinmiyor'),
                "dogru_cevap": report_data.get('dogru_cevap', 0),
                "yanlis_cevap": report_data.get('yanlis_cevap', 0),
                "bos_cevap": report_data.get('bos_cevap', 0),
                "toplam_soru": report_data.get('toplam_soru', 0),
                "yuzde": float(report_data.get('yuzde', 0.0)),
                "sure": float(report_data.get('sure', 0.0))
            }

            response = requests.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=60  # Gemini API yavaş olabilir
            )
            response.raise_for_status()
            
            result = response.json()
            report_text = result.get('rapor_metni', 'Rapor oluşturulamadı.')
            
            # App'e result_id'yi kaydet (gelecekteki kullanım için)
            app = MDApp.get_running_app()
            if hasattr(app, 'last_test_result'):
                app.last_test_result['result_id'] = result.get('result_id')
            
            return report_text

        except Exception as e:
            print(f"Yeni rapor oluşturulurken hata: {e}")
            raise

    def _update_report_ui(self, report_data, analysis_text):
        """UI'yi güncellenmiş rapor ile günceller"""
        full_report_text = f"""
[b]Öğrenci:[/b] {report_data.get('ogrenci_adi', 'Bilinmiyor')}
[b]Konu:[/b] {report_data.get('konu', 'Bilinmiyor')}
[b]Toplam Soru:[/b] {report_data.get('toplam_soru', 0)}
[b]Doğru:[/b] {report_data.get('dogru_cevap', 0)}
[b]Yanlış:[/b] {report_data.get('yanlis_cevap', 0)}
[b]Boş:[/b] {report_data.get('bos_cevap', 0)}
[b]Başarı Yüzdesi:[/b] %{report_data.get('yuzde', 0.0)}
[b]Süre:[/b] {report_data.get('sure', 0)} saniye

[b]Detaylı Analiz:[/b]
{analysis_text}
"""
        if self.ids.report_content:
            self.ids.report_content.text = full_report_text.strip()

    def refresh_report(self):
        """Raporu yeniden yükler (manuel refresh için)"""
        self.student_name_text = "Yenileniyor..."
        Clock.schedule_once(self.load_report_data, 0.1)

    def export_report(self):
        """Raporu dışa aktarma fonksiyonu (gelecek geliştirme için)"""
        if self.ids.report_content:
            report_content = self.ids.report_content.text
            # TODO: PDF export, file sharing vb. implementasyonu
            show_popup("Bilgi", "Rapor dışa aktarma özelliği yakında eklenecek.")
        else:
            show_popup("Hata", "Dışa aktarılacak rapor bulunamadı.")
