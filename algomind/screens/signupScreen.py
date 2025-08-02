
from kivy.uix.screenmanager import Screen
from kivy.app import App
from algomind.helpers import show_popup, clear_text_inputs

class SignUpScreen(Screen):
    """
    Kullanıcıların yeni bir hesap oluşturmasını sağlayan ekran.

    Kullanıcıdan ad, soyad, kullanıcı adı, e-posta ve şifre gibi bilgileri alır.
    Girilen bilgileri doğrular ve sunucuya göndererek yeni bir kullanıcı oluşturur.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_role = 'ogretmen'  # Default role

    def do_signup(self, email, password, password_confirm, role, username, first_name, last_name):
        """
        Kullanıcı kayıt işlemini gerçekleştirir.

        Args:
            email (str): Kullanıcının e-posta adresi.
            password (str): Kullanıcının şifresi.
            password_confirm (str): Kullanıcının şifre tekrarı.
            role (str): Kullanıcının rolü (öğretmen veya veli).
            username (str): Kullanıcının kullanıcı adı.
            first_name (str): Kullanıcının adı.
            last_name (str): Kullanıcının soyadı.
        """
        if not all([email, password, password_confirm, role, username, first_name, last_name]):
            show_popup("Hata", "Lütfen tüm alanları doldurun.")
            return

        if password != password_confirm:
            show_popup("Hata", "Şifreler eşleşmiyor.")
            return

        app = App.get_running_app()
        success, message = app.create_user(email, password, role, username, first_name, last_name)

        if success:
            show_popup("Başarılı", "Hesap başarıyla oluşturuldu!")
            app.root.ids.screen_manager.current = 'login_screen'
            # Clear fields after successful signup and screen transition
            clear_text_inputs(self, ["ad", "soyad", "username", "email", "password", "password_confirm"])
        else:
            show_popup("Hata", message)

    def on_leave(self):
        """Ekrandan ayrılırken alanları temizler."""
        clear_text_inputs(self, ["ad", "soyad", "username", "email", "password", "password_confirm"])
