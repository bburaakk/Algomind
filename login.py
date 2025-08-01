from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from algomind.data import database
from algomind.helpers import show_popup
from kivymd.app import MDApp


class LoginScreen(Screen):
    selected_role = StringProperty('ogretmen')

    def do_login(self, login_text, password_text):
        if not login_text or not password_text:
            show_popup("Giriş Hatası", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        # FastAPI üzerinden giriş kontrolü
        success, message = database.auth_service.login(login_text, password_text)

        if success:
            # Token alındı, şimdi kullanıcı rolünü çek
            role = database.auth_service.get_user_role()
            if role != self.selected_role:
                show_popup("Rol Hatası", f"Giriş yaptığınız kullanıcı {role} rolünde.")
                return

            app = MDApp.get_running_app()
            app.logged_in_user = login_text
            app.user_role = role

            if role == 'teacher':
                self.manager.current = 'ogrenciEkleSec'
            elif role == 'parent':
                self.manager.current = 'test_screen'
            else:
                show_popup("Giriş Hatası", f"Bilinmeyen kullanıcı rolü: {role}")
        else:
            show_popup("Giriş Hatası", message)

    def clear_fields(self):
        self.ids.login.text = ""
        self.ids.password.text = ""

    def on_enter(self, *args):
        self.ids.login.focus = True
