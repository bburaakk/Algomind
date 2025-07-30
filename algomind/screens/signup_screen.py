from kivy.uix.screenmanager import Screen

# Gerekli modülleri yeni yerlerinden import ediyoruz
from algomind.data import database
from algomind.helpers import show_popup


class SignUpScreen(Screen):
    def do_signup(self, username, password, password_confirm):
        if not username or not password:
            show_popup("Kayıt Hatası", "Kullanıcı adı ve şifre alanları boş bırakılamaz.")
            return

        if len(password) < 4:
            show_popup("Kayıt Hatası", "Şifre en az 4 karakter olmalıdır.")
            return

        if password != password_confirm:
            show_popup("Kayıt Hatası", "Şifreler uyuşmuyor.")
            return

        success, message = database.create_user(username, password)

        if success:
            print(f"Yeni kullanıcı kaydı başarılı: Kullanıcı Adı='{username}'")
            show_popup("Başarılı", "Kayıt tamamlandı!\nLütfen giriş yapın.")
            self.manager.current = 'login_screen'
        else:
            print(f"Kayıt hatası: {message}")
            show_popup("Kayıt Hatası", message)

    def on_leave(self, *args):
        """Ekrandan ayrılırken input alanlarını temizler."""
        print("SignUpScreen'den ayrılındı, alanlar temizleniyor.")
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.password_confirm.text = ""
