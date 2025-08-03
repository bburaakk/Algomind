"""
Rapor Ekranı
=============

Bu modül, KivyMD uygulamasının rapor ekranını yönetir.
Gemini tarafından oluşturulan öğrenci gelişim raporlarını gösterir.
"""

from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivymd.app import MDApp

class RaporEkrani(MDScreen):
    """
    Öğrenci gelişim raporlarını gösteren ekran.

    Bu ekran, Gemini'den alınan analizi temel alarak öğrencinin güçlü yönlerini,
    gelişim alanlarını ve önerileri gösterir.
    """

    def on_pre_enter(self, *args):
        """
        Ekran görüntülenmeden hemen önce çağrılır.
        Rapor verilerini yüklemek için kullanılır.
        """
        # Raporun hemen yüklenmesi için Clock.schedule_once kullanıyoruz.
        # Bu, ekranın çizilmesini beklemeden verilerin yerleştirilmesini sağlar.
        Clock.schedule_once(self.fetch_and_display_report)
        super().on_pre_enter(*args)

    def fetch_and_display_report(self, *args):
        """
        Gemini'den raporu alır (simüle eder) ve ekrandaki etiketleri günceller.
        """
        app = MDApp.get_running_app()
        # TODO: Bu kısım, gerçek Gemini API çağrısı ile değiştirilecek.
        # Şimdilik, tasarımın nasıl görüneceğini test etmek için sahte veri kullanıyoruz.
        mock_gemini_report = {
            "strengths": (
                "- **Görsel Hafıza:** Resimli kart eşleştirme testlerinde %95 başarı.\\n"
                "- **Desen Tanıma:** Şekil tamamlama görevlerinde hızlı ve doğru yanıtlar veriyor.\\n"

                "- **Odaklanma:** Tek bir göreve uzun süre odaklanabilme becerisi gösteriyor."
            ),
            "development_areas": (
                "- **Sözel İfade:** Duygularını ve düşüncelerini ifade etmekte zorlanabiliyor.\\n"
                "- **Sosyal Etkileşim:** Grup aktivitelerine katılmakta çekingen davranıyor.\\n"
                "- **Sıralama Becerisi:** Olayları kronolojik sıraya koyma konusunda desteğe ihtiyaç duyuyor."
            ),
            "recommendations": (
                "- **Hikaye Kartları:** Olay sıralama becerisini geliştirmek için resimli hikaye kartları kullanılabilir.\\n"
                "- **Duygu Kartları:** Farklı duyguları ifade eden yüz resimleriyle duyguları tanıma ve isimlendirme çalışmaları yapılabilir.\\n"
                "- **Rol Yapma Oyunları:** Basit sosyal senaryolarla (örn: selamlaşma, bir şey isteme) etkileşim becerileri desteklenebilir.Burdan sonrasını deneme olarak ekliyorum. Bir zamalar iki insan takılıyormuş bunlar çok iyi arkadaş olmuş. Taa ki gökten bir yaratık gelene kadar."
            )
        }

        # .kv dosyasındaki ilgili widget'ların ID'lerini kullanarak metinleri güncelliyoruz.
        if self.ids:
            self.ids.student_name_label.text = getattr(app, 'selected_student_name', 'Öğrenci Bulunamadı')
            self.ids.strengths_label.text = mock_gemini_report.get("strengths", "Veri yok.")
            self.ids.development_areas_label.text = mock_gemini_report.get("development_areas", "Veri yok.")
            self.ids.recommendations_label.text = mock_gemini_report.get("recommendations", "Veri yok.")
