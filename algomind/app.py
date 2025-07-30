from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from algomind.screens import test_screen, ogrenciEkleSec
from algomind.screens import rapor_ekrani
from algomind.screens import signup_screen
from algomind.screens import login_screen
from algomind.screens import test_secim
from algomind.screens import profile
from algomind.data import database

class TestApp(App):
    title = "Algomind"
    logged_in_user = StringProperty('')

    def build(self):
        database.init_db_users()

        Builder.load_file('algomind/UI/screens/loginscreen.kv')
        Builder.load_file('algomind/UI/screens/signupscreen.kv')
        Builder.load_file('algomind/UI/screens/testscreen.kv')
        Builder.load_file('algomind/UI/screens/raporekrani.kv')
        Builder.load_file('algomind/UI/screens/profile.kv')
        Builder.load_file('algomind/UI/screens/test_secim.kv')
        Builder.load_file('algomind/UI/screens/ogrenciEkleSec.kv')

        sm = ScreenManager()
        sm.add_widget(login_screen.LoginScreen(name='login_screen'))
        sm.add_widget(signup_screen.SignUpScreen(name='signup_screen'))
        sm.add_widget(test_screen.TestScreen(name='test_screen'))
        sm.add_widget(rapor_ekrani.RaporEkrani(name='rapor_ekrani'))
        sm.add_widget(profile.ProfileEkrani(name='profile'))
        sm.add_widget(test_secim.TestSecimEkrani(name='test_secim'))
        sm.add_widget(ogrenciEkleSec.OgrenciYonetimEkrani(name='ogrenciEkleSec'))
        # sm.current = 'ogrenciEkleSec'
        return sm


