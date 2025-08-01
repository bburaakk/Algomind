from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from algomind.data import database
from algomind.helpers import show_popup
from kivymd.app import MDApp  # MDApp'e erişim için import ettik.


class LoginScreen(Screen):
    # Giriş yapan kullanıcının rolünü tutacak property
    selected_role = StringProperty('ogretmen')

    def do_login(self, login_text, password_text):
        if not login_text or not password_text:
            show_popup("Giriş Hatası", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        # DÜZELTME: Veri tabanı doğrulamasında rolü de parametre olarak gönderiyoruz.
        if database.verify_user(login_text, password_text, self.selected_role):
            app = MDApp.get_running_app()
            app.logged_in_user = login_text
            app.user_role = self.selected_role

            # DÜZELTME: Kullanıcı rolüne göre farklı ana ekranlara yönlendiriyoruz.
            if self.selected_role == 'ogretmen':
                self.manager.current = 'ogrenciEkleSec'
            elif self.selected_role == 'veli':
                # Veli için ayrı bir ana ekran oluşturulursa buraya eklenecek.
                self.manager.current = 'test_screen'
        else:
            show_popup("Giriş Hatası", "Kullanıcı adı, şifre veya rol hatalı.")

    def clear_fields(self):
        self.ids.login.text = ""
        self.ids.password.text = ""

    def on_enter(self, *args):
        self.ids.login.focus = True

