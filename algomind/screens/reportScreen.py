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
        # Debug: report_data içeriğini logla
        print(f"DEBUG: report_data içeriği: {report_data}")
        
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

            # Option 2: Yeni rapor oluştur (backend'den)
            try:
                report_text = self._create_new_report(report_data)
                Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
                return
            except Exception as backend_error:
                print(f"Backend rapor oluşturma başarısız: {backend_error}")
                # Fallback: Lokal rapor oluştur
                report_text = self._generate_local_report(report_data)
                Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
                return

        except requests.exceptions.ConnectionError as e:
            print(f"Backend'e bağlanırken bağlantı hatası: {e}")
            # Fallback: Lokal rapor oluştur
            report_text = self._generate_local_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
        
        except requests.exceptions.Timeout as e:
            print(f"Backend timeout hatası: {e}")
            report_text = self._generate_local_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
        
        except requests.exceptions.HTTPError as e:
            print(f"Backend HTTP hatası: {e}")
            # Response body'sini de logla
            try:
                error_detail = e.response.json() if e.response else {}
                print(f"Hata detayı: {error_detail}")
            except:
                print(f"Response text: {e.response.text if e.response else 'No response'}")
            
            # Fallback: Lokal rapor oluştur
            report_text = self._generate_local_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
        
        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {e}")
            report_text = self._generate_local_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))
        
        except Exception as e:
            print(f"Beklenmedik hata: {e}")
            report_text = self._generate_local_report(report_data)
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, report_text))

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

    def _get_latest_test_id(self):
        """Backend'den en son test ID'sini getirir"""
        try:
            url = f"{API_BASE_URL}/tests/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            tests = response.json()
            
            if tests:
                # En son test ID'sini bul
                latest_test = max(tests, key=lambda x: x.get('id', 0))
                return latest_test.get('id')
            return None
        except Exception as e:
            print(f"Latest test ID alınırken hata: {e}")
            return None
        """Backend'de yeni rapor oluşturur"""
        try:
            # Test sonucu ve rapor oluştur
            url = f"{API_BASE_URL}/create_test_result_and_report"
            
    def _create_new_report(self, report_data):
        """Backend'de yeni rapor oluşturur"""
        try:
            # Test sonucu ve rapor oluştur
            url = f"{API_BASE_URL}/create_test_result_and_report"
            
            # Test ID'yi doğru şekilde al
            app = MDApp.get_running_app()
            last_test_id = getattr(app, 'last_saved_test_id', None)
            
            print(f"DEBUG: app'den alınan last_test_id: {last_test_id}")
            print(f"DEBUG: report_data'dan test_id: {report_data.get('test_id')}")
            
            # Eğer app'de kayıtlı test_id yoksa, backend'den en son test ID'sini al
            final_test_id = last_test_id
            if not final_test_id:
                print("DEBUG: App'de test_id yok, backend'den en son test ID'si alınıyor...")
                final_test_id = self._get_latest_test_id()
            
            # Hala bulamadıysak, report_data'daki değeri kullan
            if not final_test_id:
                final_test_id = report_data.get('test_id', 1)
                print(f"DEBUG: Backend'den de alınamadı, report_data'daki değer kullanılıyor: {final_test_id}")
            
            payload = {
                "test_id": final_test_id,
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

            print(f"DEBUG: Final payload gönderiliyor: {payload}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=60  # Gemini API yavaş olabilir
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {response.headers}")
            print(f"DEBUG: Response text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            report_text = result.get('rapor_metni', 'Rapor oluşturulamadı.')
            
            # App'e result_id'yi kaydet (gelecekteki kullanım için)
            if hasattr(app, 'last_test_result'):
                app.last_test_result['result_id'] = result.get('result_id')
            
            return report_text

        except Exception as e:
            print(f"Yeni rapor oluşturulurken hata: {e}")
            raise
            
            response = requests.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=60  # Gemini API yavaş olabilir
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {response.headers}")
            print(f"DEBUG: Response text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            report_text = result.get('rapor_metni', 'Rapor oluşturulamadı.')
            
            # App'e result_id'yi kaydet (gelecekteki kullanım için)
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

    def _generate_local_report(self, report_data):
        """Backend erişilemediğinde lokal rapor oluşturur"""
        ogrenci_adi = report_data.get('ogrenci_adi', 'Bilinmiyor')
        konu = report_data.get('konu', 'Test')
        dogru = report_data.get('dogru_cevap', 0)
        yanlis = report_data.get('yanlis_cevap', 0)
        toplam = report_data.get('toplam_soru', 0)
        yuzde = report_data.get('yuzde', 0.0)
        sure = report_data.get('sure', 0)

        # Basit performans değerlendirmesi
        if yuzde >= 80:
            performance_level = "Mükemmel"
            encouragement = "Harika bir performans sergiledi!"
        elif yuzde >= 60:
            performance_level = "İyi"
            encouragement = "Başarılı bir performans gösterdi."
        elif yuzde >= 40:
            performance_level = "Orta"
            encouragement = "Gelişim gösteriyor, biraz daha çalışmayla daha iyi sonuçlar alabilir."
        else:
            performance_level = "Gelişime Açık"
            encouragement = "Bu konuda daha fazla pratik yapmasında fayda var."

        # Süre analizi
        if sure > 0:
            sure_dakika = sure / 60
            if sure_dakika < 5:
                sure_analizi = "Hızlı cevap verme becerisi gösterdi."
            elif sure_dakika < 10:
                sure_analizi = "Uygun bir sürede test tamamlandı."
            else:
                sure_analizi = "Daha dikkatli düşünerek cevap vermeyi tercih etti."
        else:
            sure_analizi = "Test süresi kaydedilemedi."

        # Konu bazlı öneriler
        konu_onerileri = {
            "Renk Tanıma Testi": "Günlük hayatta renkleri fark etmeye ve isimlendirmeye odaklanmasında fayda var. Boyama aktiviteleri ve renk eşleştirme oyunları öneriyoruz.",
            "Matematik Testi": "Temel matematik becerileri için günlük pratik önemli. Sayma oyunları ve basit hesap makinesi kullanımı faydalı olabilir.",
            "Eş ve Zıt Anlamlı Kelimeler Testi": "Kelime hazinesi geliştirmek için kitap okuma ve kelime oyunları öneriyoruz.",
            "Hayvan Tanıma Testi": "Doğa belgeselleri izlemek ve hayvanat bahçesi ziyaretleri öğrenmeyi destekleyecektir.",
            "Nesne Tanıma Testi": "Çevresindeki nesneleri tanımlama ve kategorileme aktiviteleri faydalı olacaktır.",
            "Yiyecekler Testi": "Sağlıklı beslenme konusunda bilinç geliştirmek için mutfak aktivitelerine katılması önerilir."
        }

        oneriler = konu_onerileri.get(konu, "Bu konuda düzenli pratik yapması gelişimini destekleyecektir.")

        local_report = f"""
📊 PERFORMANS DEĞERLENDİRMESİ

🎯 Genel Durum: {performance_level}
{ogrenci_adi} {konu.lower()} konusunda {encouragement}

📈 Detaylı Analiz:
• Toplam {toplam} sorudan {dogru} tanesini doğru yanıtladı
• Başarı oranı: %{yuzde}
• {sure_analizi}

🎈 Güçlü Yönler:
• Test süresince konsantrasyonunu korudu
• Sorulara cevap verme konusunda istekli davrandı
• {konu.lower()} konusunda temel bilgi düzeyine sahip

🌟 Gelişim Önerileri:
{oneriler}

💪 Motivasyon:
Her çocuk kendi hızında öğrenir ve gelişir. {ogrenci_adi}'nin gösterdiği çaba takdire şayandır. Düzenli pratik ve destekle başarısını artıracağından eminiz!

[Not: Bu rapor geçici olarak yerel sistem tarafından oluşturulmuştur.]
"""
        return local_report
