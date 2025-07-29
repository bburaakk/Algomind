from kivy.uix.screenmanager import Screen

# Veritabanı ve yardımcı fonksiyonları yeni yerlerinden import ediyoruz.
# Bu yolların çalışması için diğer adımları da tamamlamamız gerekecek.
from algomind.data import database
from algomind.helpers import show_popup


class LoginScreen(Screen):
    def do_login(self, login_text, password_text):
        if not login_text or not password_text:
            show_popup("Giriş Hatası", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        if database.verify_user(login_text, password_text):
            print(f"Giriş başarılı: Kullanıcı Adı='{login_text}'")
            self.manager.current = 'ogrenci_ekle_ekrani'
        else:
            print(f"Giriş başarısız: Kullanıcı Adı='{login_text}'")
            show_popup("Giriş Hatası", "Kullanıcı adı veya şifre hatalı.")

    def on_leave(self, *args):
        """Ekrandan ayrılırken input alanlarını temizler."""
        print("LoginScreen'den ayrılındı, alanlar temizleniyor.")
        self.ids.login.text = ""
        self.ids.password.text = ""