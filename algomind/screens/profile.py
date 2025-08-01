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
    # Geri dönülecek ekranın adını tutmak için yeni bir property.
    return_to_screen = StringProperty(None)

    def on_enter(self, *args):
        """Ekran açıldığında, giriş yapmış olan kullanıcının adını alır ve ekrana yazar."""
        self.username = App.get_running_app().logged_in_user

    def cikis_yap(self):
        """
        Kullanıcıyı çıkış yaparak login ekranına yönlendirir.
        """
        # ScreenManager üzerinden ekran değiştirme
        self.manager.current = 'login_screen'

    def geri_git(self):
        """
        Kullanıcıyı, bu ekrana gelmeden önce belirtilen ekrana yönlendirir.
        """
        # Eğer bir önceki ekran belirtilmişse oraya dön.
        if self.return_to_screen:
            # Geri animasyonunun sağa doğru olması daha doğal bir his verir.
            self.manager.transition.direction = 'right'
            self.manager.current = self.return_to_screen
        else:
            # Eğer return_to_screen ayarlanmamışsa, güvenli bir varsayılan ekrana dön.
            # Bu durum normalde yaşanmamalı, ancak bir önlem olarak eklendi.
            print("UYARI: ProfileEkrani.return_to_screen ayarlanmamış. Varsayılan ekrana dönülüyor.")
            self.manager.current = 'test_secim'