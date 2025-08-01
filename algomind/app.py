from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp

# Ekran sınıflarını import edelim
from algomind.screens.login_screen import LoginScreen
from algomind.screens.signup_screen import SignUpScreen
from algomind.screens.test_screen import TestScreen
from algomind.screens.rapor_ekrani import RaporEkrani
from algomind.screens.profile import ProfileEkrani
from algomind.screens.test_secim import TestSecimEkrani
from algomind.screens.ogrenciEkleSec import OgrenciYonetimEkrani
from algomind.data import database


class TestApp(MDApp):
    title = "Algomind"
    logged_in_user = StringProperty('')
    user_role = StringProperty('')  # Kullanıcının rolü için property

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # DÜZELTME: Veritabanı başlatma işlemi, KV dosyaları yüklenmeden önce yapılmalıdır.
        database.init_db_users()

        # Tüm ekranları yükle
        Builder.load_file('algomind/UI/screens/raporekrani.kv')
        Builder.load_file('algomind/UI/screens/loginscreen.kv')
        Builder.load_file('algomind/UI/screens/signupscreen.kv')
        Builder.load_file('algomind/UI/screens/testscreen.kv')
        Builder.load_file('algomind/UI/screens/profile.kv')
        Builder.load_file('algomind/UI/screens/test_secim.kv')
        Builder.load_file('algomind/UI/screens/ogrenciEkleSec.kv')

        # Ana layout'u oluştur.
        main_layout = Builder.load_string("""
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

            # DÜZELTME: Artık rol bazlı menüler kaldırıldı.
            # Öğretmen ve Veli tüm menü öğelerini görecek.
            MDList:
                id: ana_menu_list
                size_hint_y: None
                height: self.minimum_height
                OneLineIconListItem:
                    text: "Profil"
                    on_release:
                        app.root.ids.screen_manager.get_screen('profile_screen').return_to_screen = app.root.ids.screen_manager.current
                        app.root.ids.screen_manager.current = 'profile_screen'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "account-circle"
                OneLineIconListItem:
                    text: "Öğrenci Yönetimi"
                    on_release:
                        app.root.ids.screen_manager.current = 'ogrenciEkleSec_screen'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "account-multiple"
                OneLineIconListItem:
                    text: "Rapor Ekranı"
                    on_release:
                        app.root.ids.screen_manager.current = 'rapor_ekrani_screen'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "file-chart"
                OneLineIconListItem:
                    text: "Test Seçimi"
                    on_release:
                        app.root.ids.screen_manager.current = 'test_secim'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "library-books"
                OneLineIconListItem:
                    text: "Test Ekranı"
                    on_release:
                        app.root.ids.screen_manager.current = 'test_screen'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "pencil-box-multiple"
                OneLineIconListItem:
                    text: "Ayarlar"
                    on_release:
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "cog"
                OneLineIconListItem:
                    text: "Çıkış Yap"
                    on_release:
                        app.root.ids.screen_manager.current = 'login_screen'
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "logout"
""")

        sm = main_layout.ids.screen_manager

        # Tüm ekranları ScreenManager'a dinamik olarak ekle.
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(SignUpScreen(name='signup_screen'))
        sm.add_widget(TestScreen(name='test_screen'))
        sm.add_widget(RaporEkrani(name='rapor_ekrani_screen'))
        sm.add_widget(ProfileEkrani(name='profile_screen'))
        sm.add_widget(TestSecimEkrani(name='test_secim'))
        sm.add_widget(OgrenciYonetimEkrani(name='ogrenciEkleSec'))

        # Başlangıç ekranını ayarla
        sm.current = 'login_screen'

        return main_layout


if __name__ == '__main__':
    TestApp().run()
