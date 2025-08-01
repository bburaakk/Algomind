from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from algomind.data import database
from algomind.helpers import show_popup
from kivymd.app import MDApp


class SignUpScreen(Screen):
    # Kayıt olan kullanıcının rolünü varsayılan olarak tutar
    selected_role = StringProperty('ogretmen')

    def do_signup(self, username, ad, soyad, password, password_confirm, email):
        """Kullanıcı kayıt işlemini yapar."""
        if not username or not ad or not soyad or not password or not email:
            show_popup("Kayıt Hatası", "Tüm alanlar boş bırakılamaz.")
            return

        if len(password) < 4:
            show_popup("Kayıt Hatası", "Şifre en az 4 karakter olmalıdır.")
            return

        if password != password_confirm:
            show_popup("Kayıt Hatası", "Şifreler uyuşmuyor.")
            return

        if self.selected_role not in ['ogretmen', 'veli']:
            show_popup("Kayıt Hatası", "Lütfen bir rol seçin (Öğretmen veya Veli).")
            return

        # DÜZELTME: Kullanıcı rolünü ve e-postayı da create_user fonksiyonuna gönderiyoruz.
        success, message = database.create_user(username, ad, soyad, email, password, role=self.selected_role)

        if success:
            print(f"Yeni kullanıcı kaydı başarılı: Kullanıcı Adı='{username}', Adı='{ad}', Soyadı='{soyad}', Email='{email}'")
            show_popup("Başarılı", "Kayıt tamamlandı!\nLütfen giriş yapın.")
            self.manager.current = 'login_screen'
        else:
            print(f"Kayıt hatası: {message}")
            show_popup("Kayıt Hatası", message)

    def on_leave(self, *args):
        """Ekrandan ayrılırken input alanlarını temizler."""
        self.ids.username.text = ""
        self.ids.ad.text = ""
        self.ids.soyad.text = ""
        self.ids.email.text = ""
        self.ids.password.text = ""
        self.ids.password_confirm.text = ""
