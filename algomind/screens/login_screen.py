# /home/burak/Belgeler/PythonProjects/Algomind/algomind/screens/login_screen.py

# 1. App sınıfını import ediyoruz
from kivy.app import App
from kivy.uix.screenmanager import Screen
from algomind.data import database
from algomind.helpers import show_popup

class LoginScreen(Screen):
    def do_login(self, login_text, password_text):
        if not login_text or not password_text:
            show_popup("Giriş Hatası", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        if database.verify_user(login_text, password_text):
            print(f"Giriş başarılı: Kullanıcı Adı='{login_text}'")

            # 2. EKSİK OLAN EN ÖNEMLİ KISIM BURASI
            # Giriş yapan kullanıcının adını ana App sınıfında saklıyoruz.
            # Bu satır olmadan, profil ekranı kimin giriş yaptığını bilemez.
            App.get_running_app().logged_in_user = login_text

            # Kullanıcıyı öğrenci seçim ekranına yönlendiriyoruz.
            # (Daha önce 'ogrenci_ekle_ekrani' idi, 'ogrenci_secim_ekrani' daha mantıklı bir akış olabilir)
            self.manager.current = 'ogrenciEkleSec'
        else:
            print(f"Giriş başarısız: Kullanıcı Adı='{login_text}'")
            show_popup("Giriş Hatası", "Kullanıcı adı veya şifre hatalı.")

    def clear_fields(self):
        """Giriş alanlarını temizlemek için yardımcı bir fonksiyon."""
        self.ids.login.text = ""
        self.ids.password.text = ""

    def on_enter(self, *args):
        # Ekrana her girildiğinde kullanıcı adı alanına odaklanmak iyi bir kullanıcı deneyimi sağlar.
        print("LoginScreen'e girildi.")
        self.ids.login.focus = True
