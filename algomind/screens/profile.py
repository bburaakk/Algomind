# /home/burak/Belgeler/PythonProjects/Algomind/algomind/screens/profile.py
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

class ProfileEkrani(Screen):
    """
    Kullanıcı profilini gösteren ekran.
    Giriş yapan kullanıcının adını gösterir ve çıkış yapma işlevini barındırır.
    """
    # .kv dosyasındaki Label'ın text özelliğine bağlanacak olan property.
    username = StringProperty('')

    def on_enter(self, *args):
        """Ekran açıldığında, giriş yapmış olan kullanıcının adını alır ve ekrana yazar."""
        self.username = App.get_running_app().logged_in_user

    def cikis_yap(self):
        """
        Kullanıcıyı çıkış yaparak login ekranına yönlendirir.
        """
        print("Çıkış yapılıyor, login ekranına geçiliyor.")
        # ScreenManager üzerinden ekran değiştirme
        self.manager.current = 'login_screen'
