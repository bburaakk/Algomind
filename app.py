from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp

# Ekran sınıfları
from algomind.screens.login_screen import LoginScreen
from algomind.screens.signup_screen import SignUpScreen
from algomind.screens.test_screen import TestScreen
from algomind.screens.rapor_ekrani import RaporEkrani
from algomind.screens.profile import ProfileEkrani
from algomind.screens.test_secim import TestSecimEkrani
from algomind.screens.ogrenciEkleSec import OgrenciYonetimEkrani
from algomind.screens.veli_ana_ekran import VeliAnaEkrani

# FastAPI destekli veri servisi
from algomind.data import database


class TestApp(MDApp):
    title = "Algomind"
    logged_in_user = StringProperty('')
    user_role = StringProperty('')

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # SQLite init kaldırıldı – çünkü FastAPI API üzerinden işlem yapıyoruz
        # database.init_db_users()

        # KV dosyalarını yükle
        Builder.load_file('algomind/UI/screens/raporekrani.kv')
        Builder.load_file('algomind/UI/screens/loginscreen.kv')
        Builder.load_file('algomind/UI/screens/signupscreen.kv')
        Builder.load_file('algomind/UI/screens/testscreen.kv')
        Builder.load_file('algomind/UI/screens/profile.kv')
        Builder.load_file('algomind/UI/screens/test_secim.kv')
        Builder.load_file('algomind/UI/screens/ogrenciEkleSec.kv')
        Builder.load_file('algomind/UI/screens/veli_ana_ekran.kv')

        # Ana layout (navigation drawer + screen manager)
        main_layout = Builder.load_string("""<YUKARIDAKİ LONG KV STRING DEĞİŞMEDEN DEVAM EDİYOR>""")

        # ScreenManager referansı
        sm = main_layout.ids.screen_manager

        # Ekranları ekle
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(SignUpScreen(name='signup_screen'))
        sm.add_widget(TestScreen(name='test_screen'))
        sm.add_widget(RaporEkrani(name='rapor_ekrani_screen'))
        sm.add_widget(ProfileEkrani(name='profile_screen'))
        sm.add_widget(TestSecimEkrani(name='test_secim'))
        sm.add_widget(OgrenciYonetimEkrani(name='ogrenciEkleSec_screen'))
        sm.add_widget(VeliAnaEkrani(name='veli_ana_ekran'))

        sm.current = 'login_screen'

        return main_layout
