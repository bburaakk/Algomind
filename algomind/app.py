from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.lang import Builder
import requests
from algomind.screens.loginScreen import LoginScreen
from algomind.screens.signupScreen import SignUpScreen
from algomind.screens.examScreen import TestScreen
from algomind.screens.reportScreen import RaporEkrani
from algomind.screens.profile import ProfileEkrani
from algomind.screens.examSelection import TestSecimEkrani
from algomind.screens.studentAddSelection import OgrenciYonetimEkrani
from algomind.helpers import clear_text_inputs


class MainApp(MDApp):
    title = "Algomind"
    logged_in_user = StringProperty('')
    user_role = StringProperty('')

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # .kv dosyalarını yükle
        Builder.load_file('algomind/UI/screens/reportScreen.kv')
        Builder.load_file('algomind/UI/screens/loginScreen.kv')
        Builder.load_file('algomind/UI/screens/signupScreen.kv')
        Builder.load_file('algomind/UI/screens/examScreen.kv')
        Builder.load_file('algomind/UI/screens/profile.kv')
        Builder.load_file('algomind/UI/screens/examSelection.kv')
        Builder.load_file('algomind/UI/screens/studentAddSelection.kv')

        # Ana layout'u string olarak yükle
        main_layout = Builder.load_string('''
MDNavigationLayout:
    id: nav_layout
    MDScreenManager:
        id: screen_manager
    MDNavigationDrawer:
        id: nav_drawer
        width: self.parent.width * 0.75
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(15)
            spacing: dp(10)
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: dp(120)
                padding: dp(10)
                Image:
                    source: 'algomind/assets/profil_resmi.png'
                    size_hint: None, None
                    size: dp(80), dp(80)
                    pos_hint: {'center_x': .5}
                MDLabel:
                    text: f"Hoş Geldin, {app.logged_in_user}" if app.logged_in_user else "Hoş Geldin, Misafir"
                    font_style: "H6"
                    halign: "center"

            # Birleştirilmiş menü listesi
            MDList:
                id: menu_list
                OneLineIconListItem:
                    text: "Profil"
                    on_release: app.switch_screen('profile_screen')
                    IconLeftWidget:
                        icon: "account-circle"
                OneLineIconListItem:
                    text: "Öğrenci Yönetimi"
                    on_release: app.switch_screen('ogrenciEkleSec')
                    IconLeftWidget:
                        icon: "account-multiple"
                OneLineIconListItem:
                    text: "Rapor Ekranı"
                    on_release: app.switch_screen('rapor_ekrani_screen')
                    IconLeftWidget:
                        icon: "file-chart"
                OneLineIconListItem:
                    text: "Test Seçimi"
                    on_release: app.switch_screen('test_secim')
                    IconLeftWidget:
                        icon: "clipboard-check-outline"

            # Ortak menü öğeleri (sadece çıkış)
            MDList:
                id: ortak_menu_list
                size_hint_y: None
                height: self.minimum_height
                OneLineIconListItem:
                    text: "Çıkış Yap"
                    on_release: app.logout()
                    IconLeftWidget:
                        icon: "logout"
''')

        sm = main_layout.ids.screen_manager
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(SignUpScreen(name='signup_screen'))
        sm.add_widget(TestScreen(name='test_screen'))
        sm.add_widget(RaporEkrani(name='rapor_ekrani_screen'))
        sm.add_widget(ProfileEkrani(name='profile_screen'))
        sm.add_widget(TestSecimEkrani(name='test_secim'))
        sm.add_widget(OgrenciYonetimEkrani(name='ogrenciEkleSec'))

        sm.current = 'login_screen'
        return main_layout

    def create_user(self, email, password, role, username, first_name, last_name):
        """
        Yeni kullanıcıyı API'ye kaydeder.
        Bu fonksiyon signupScreen tarafından çağırılır.
        """
        # Sunucu adresinizin doğru olduğundan emin olun
        url = "http://35.202.188.175:8080/signup"
        user_data = {
            "email": email,
            "password": password,
            "role": role,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        try:
            # Sunucuya POST isteği gönder
            response = requests.post(url, json=user_data)

            # Başarılı yanıt (200 veya 201 genellikle başarılıdır)
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Kayıt başarılı:", response.json())
                return True, "Kayıt başarılı!"
            # Hatalı yanıt
            else:
                error_message = f"Hata: {response.status_code} - {response.text}"
                print(f"❌ Kayıt hatası: {error_message}")
                return False, error_message

        except requests.exceptions.RequestException as e:
            # Bağlantı hatası (sunucuya ulaşılamıyor vb.)
            error_message = f"Bağlantı hatası: {e}"
            print(f"❌ Ağ hatası: {error_message}")
            return False, error_message

    def switch_screen(self, screen_name):
        self.root.ids.screen_manager.current = screen_name
        self.root.ids.nav_drawer.set_state("close")

    def logout(self):
        self.user_role = ''
        self.logged_in_user = ''
        login_screen = self.root.ids.screen_manager.get_screen('login_screen')
        clear_text_inputs(login_screen, ['login', 'password'])
        self.switch_screen('login_screen')

    def login_successful(self, user_info):
        self.user_data = {
            "name": user_info.get("name"),
            "surname": user_info.get("surname"),
            "email": user_info.get("email"),
            "user_role": user_info.get("user_role")
        }
