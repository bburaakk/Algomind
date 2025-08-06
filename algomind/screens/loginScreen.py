from kivy.uix.screenmanager import Screen
from algomind.data import database
from algomind.helpers import show_popup
from kivymd.app import MDApp


class LoginScreen(Screen):
    """
    Kullanıcı giriş ekranı.
    Bu ekran, kullanıcıların kullanıcı adı ve şifreleri ile sisteme giriş
    yapmalarını sağlar. Ayrıca demo girişleri için de metodlar içerir.
    """

    def do_login(self, login_text, password_text):
        """
        Kullanıcı giriş işlemini gerçekleştirir.
        Kullanıcı adı ve şifreyi alarak veritabanı üzerinden kimlik doğrulaması
        yapar. Başarılı olursa, kullanıcı rolünü alır ve ilgili ana ekrana
        yönlendirir. Başarısız olursa, bir hata mesajı gösterir.
        Args:
            login_text (str): Kullanıcının girdiği kullanıcı adı.
            password_text (str): Kullanıcının girdiği şifre.
        """
        if not login_text or not password_text:
            show_popup("Giriş Hatası", "Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        # FastAPI üzerinden giriş kontrolü
        success, user_data = database.auth_service.login(login_text, password_text)
        if success:
            # Kullanıcı bilgilerini ayrı olarak al
            user_info = database.auth_service.get_user_info()
            role = database.auth_service.get_user_role()

            if role in ('ogretmen', 'veli'):
                app = MDApp.get_running_app()
                app.logged_in_user = login_text
                app.user_role = role

                # user_info'dan user_id'yi al (endpoint 'id' döndürüyor)
                if user_info and isinstance(user_info, dict):
                    app.user_id = user_info.get('id')
                else:
                    app.user_id = None
                    print("⚠ Kullanıcı ID'si alınamadı!")

                # Kullanıcı verilerini ayarla
                user_data_dict = {
                    "name": login_text,  # Geçici olarak kullanıcı adını kullan
                    "surname": "",  # Soyisim bilgisi yok
                    "email": "",  # E-posta bilgisi yok
                    "user_role": role,
                    "user_id": app.user_id
                }
                app.login_successful(user_data_dict)

                self.manager.current = 'ogrenciEkleSec'
            else:
                show_popup("Giriş Hatası", f"Bilinmeyen veya desteklenmeyen kullanıcı rolü: {role}")
        else:
            show_popup("Giriş Hatası", str(user_data))

    def on_enter(self, *args):
        """
        Ekran görüntülendiğinde çağrılır.
        Kullanıcı adı alanına odaklanır.
        """
        self.ids.login.focus = True