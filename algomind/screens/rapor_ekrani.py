# /home/burak/Belgeler/PythonProjects/Algomind/algomind/screens/rapor_ekrani.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

class RaporEkrani(Screen):
    """
    Test sonuçlarını ve raporları gösteren ekran.
    .kv dosyasındaki 'report_text_content' id'li Label'a bağlanır.
    """
    report_text_content = ObjectProperty(None)

    def on_enter(self, *args):
        """Ekran açıldığında rapor içeriğini günceller."""
        # Bu kısma raporu oluşturacak veya veritabanından çekecek
        # kodunuzu ekleyebilirsiniz.
        if self.report_text_content:
            self.report_text_content.text = "Rapor içeriği buraya dinamik olarak yüklenecek.\n\nÖrnek Rapor:\n- Test Tarihi: 2024-01-01\n- Sonuç: Başarılı"
        print("Rapor ekranına girildi.")

    def go_back_to_selection(self):
        """Kullanıcıyı öğrenci veya test seçim ekranına geri yönlendirir."""
        self.manager.current = 'test_secim'
        print("Geri butonuna basıldı, 'test_secim' ekranına geçiliyor.")

    def on_profile_button_press(self):
        """Kullanıcıyı profil ekranına yönlendirir."""
        self.manager.current = 'profile'
        print("Profil butonuna basıldı, 'profile' ekranına geçiliyor.")