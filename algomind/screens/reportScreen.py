"""
Rapor Ekranı
=============

Bu modül, KivyMD uygulamasının rapor ekranını yönetir.
Test sonuçlarını ve Gemini tarafından oluşturulan öğrenci gelişim raporlarını gösterir.
"""

from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.app import MDApp
import threading

from algomind.helpers import generate_report_comment, show_popup

class RaporEkrani(MDScreen):
    """
    Test sonuçlarını ve Gemini analizini gösteren ekran.
    """
    # .kv dosyasından gelen öğrenci adı için
    student_name_text = StringProperty("Öğrenci Raporu")

    def on_enter(self, *args):
        """
        Ekran görüntülendiğinde rapor verilerini yükler.
        """
        app = MDApp.get_running_app()
        report_data = getattr(app, 'last_test_result', None)

        if not report_data:
            show_popup("Hata", "Görüntülenecek rapor verisi bulunamadı.")
            # Rapor verisi yoksa, içeriği temizle
            if self.ids.report_content:
                self.ids.report_content.text = "Rapor verisi yok."
            return

        self.student_name_text = f"{report_data.get('ogrenci_adi', 'Bilinmiyor')} Raporu"
        
        # Rapor içeriğini ve Gemini yorumunu yükle
        self.fetch_and_display_report(report_data)
        super().on_enter(*args)

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

    def _fetch_gemini_comment_thread(self, report_data):
        """
        helpers.py'deki fonksiyonu kullanarak Gemini'den yorumu alır.
        """
        gemini_comment = generate_report_comment(report_data)
        # UI güncellemesini ana thread'de yap
        Clock.schedule_once(lambda dt: self._update_report_ui(report_data, gemini_comment))

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
