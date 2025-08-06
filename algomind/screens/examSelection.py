from algomind.screens.baseScreen import BaseScreen
from kivymd.app import MDApp


class TestSecimEkrani(BaseScreen):
    """
    Test seçim ekranı.

    Bu ekran, kullanıcıların mevcut testler arasından birini seçip
    başlatmalarını sağlar.
    """

    def go_to_profile(self):
        """Profil ekranına geçiş yapar."""
        # Profil ekranına gitmeden önce, geri dönülecek ekranı ayarla.
        # Bu fonksiyon artık menüden çağrılacağı için bu kodlara gerek kalmamıştır.
        # Menüden geçişler ana ScreenManager tarafından yönetilecektir.
        pass

    def go_to_test_screen(self):
        """Test ekranına geçiş yapar."""
        self.manager.current = 'test_screen'

    def toggle_navigation_drawer(self):
        """Gezinme menüsünü (navigation drawer) açıp kapatır."""
        # Ana MDApp objesine erişim
        app = MDApp.get_running_app()
        nav_drawer = app.root.ids.nav_drawer
        nav_drawer.set_state("open" if nav_drawer.state == "close" else "close")
