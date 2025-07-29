from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from algomind.screens import test_screen
from algomind.screens import rapor_ekrani
from algomind.screens import ogrenci_ekle_ekrani
from algomind.screens import signup_screen
from algomind.screens import login_screen
from algomind.data import database

class TestApp(App):
    title = "Algomind"

    def build(self):
        database.init_db()

        Builder.load_file('algomind/UI/screens/signupscreen.kv')
        Builder.load_file('algomind/UI/screens/loginscreen.kv')
        Builder.load_file('algomind/UI/screens/testscreen.kv')
        Builder.load_file('algomind/UI/screens/raporekrani.kv')
        Builder.load_file('algomind/UI/screens/ogrenciekle.kv')

        sm = ScreenManager()
        sm.add_widget(login_screen.LoginScreen(name='login_screen'))
        sm.add_widget(signup_screen.SignUpScreen(name='signup_screen'))
        sm.add_widget(test_screen.TestScreen(name='test_screen'))
        sm.add_widget(rapor_ekrani.RaporEkrani(name='rapor_ekrani'))
        sm.add_widget(ogrenci_ekle_ekrani.OgrenciEkleEkrani(name='ogrenci_ekle_ekrani'))
        return sm


