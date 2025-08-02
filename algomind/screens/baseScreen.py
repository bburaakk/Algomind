from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from algomind.helpers import show_popup
from algomind.data.screen_permissions import can_access_screen


class BaseScreen(Screen):
    """
    Tüm ekranlar için temel sınıf.

    Bu sınıf, ekranlara erişim kontrolü gibi ortak işlevleri sağlar.
    Tüm diğer ekran sınıfları bu sınıftan türetilmelidir.
    """
    def on_pre_enter(self, *args):
        """
        Ekran görüntülenmeden hemen önce çağrılır.

        Bu metod, kullanıcının mevcut ekrana erişim izni olup olmadığını kontrol eder.
        Eğer kullanıcının rolü (öğretmen/veli) ekran için yetkilendirilmemişse,
        bir hata mesajı gösterir ve kullanıcıyı uygun bir ekrana yönlendirir.

        Args:
            *args: Kivy tarafından gönderilen argümanlar.

        Returns:
            bool: Kullanıcının ekrana erişimi varsa True, aksi takdirde False.
        """
        app = MDApp.get_running_app()

        # Erişim kontrolü yap
        if not can_access_screen(app.user_role, self.name):
            show_popup("Erişim Hatası", "Bu sayfaya erişim yetkiniz bulunmamaktadır.")

            # Kullanıcıyı rolüne göre ana sayfaya veya giriş ekranına yönlendir
            if app.user_role in ('ogretmen', 'veli'):
                app.root.ids.screen_manager.current = 'ogrenciEkleSec'
            else:
                app.root.ids.screen_manager.current = 'login_screen'
            return False

        return super().on_pre_enter(*args)
