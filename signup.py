from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from algomind.data import database
from algomind.helpers import show_popup
from kivymd.app import MDApp


class SignUpScreen(Screen):
    selected_role = StringProperty('ogretmen')

    def do_signup(self, username, ad, soyad, password, password_confirm, email):
        if not username or not ad or not soyad or not password or not email:
            show_popup("Kayıt Hatası", "Tüm alanları doldurmalısınız.")
            return

        if len(password) < 4:
            show_popup("Kayıt Hatası", "Şifre en az 4 karakter olmalı.")
            return

        if password != password_confirm:
            show_popup("Kayıt Hatası", "Şifreler uyuşmuyor.")
            return

        if self.selected_role not in ['ogretmen', 'veli']:
            show_popup("Kayıt Hatası", "Lütfen geçerli bir rol seçin.")
            return

        # FastAPI üzerinden kullanıcı kaydı
        success, message = database.auth_service.register(
            email=email,
            password=password,
            role=self.selected_role
        )

        if success:
            print(f"Kayıt başarılı: {email} ({self.selected_role})")
            show_popup("Başarılı", "Kayıt tamamlandı. Lütfen giriş yapın.")
            self.manager.current = 'login_screen'
        else:
            print(f"Kayıt başarısız: {message}")
            show_popup("Kayıt Hatası", message)

    def on_leave(self, *args):
        self.ids.username.text = ""
        self.ids.ad.text = ""
        self.ids.soyad.text = ""
        self.ids.email.text = ""
        self.ids.password.text = ""
        self.ids.password_confirm.text = ""
