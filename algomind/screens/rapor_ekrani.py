from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty


class RaporEkrani(MDScreen):
    """
    Grafikleri ve detaylı analizleri gösteren ana rapor ekranı.
    İçeriği ve yapısı 'rapor_ekrani.kv' dosyasında tanımlanmıştır.
    """
    # .kv dosyasındaki Label'a Python'dan erişmek için bu property'yi tutabiliriz.
    # Gelecekte rapor içeriğini dinamik olarak değiştirmek için kullanışlıdır.
    report_text_content = ObjectProperty(None)

    # Bu metot, menüdeki "Profil" butonuna basıldığında çağrılır.
    def navigate_to_profile(self):
        print("Profil ekranına geçiliyor.")
        # app.root.ids.screen_manager'a erişim
        sm = self.parent.parent.ids.screen_manager
        sm.current = 'profile'
        # Menüyü kapat
        self.parent.parent.ids.nav_drawer.set_state("close")

    # Bu metot, menüdeki "Ayarlar" butonuna basıldığında çağrılır.
    def navigate_to_settings(self):
        print("Ayarlar ekranına geçiliyor.")
        # Bu fonksiyon gelecekte bir ayarlar ekranı eklendiğinde kullanılabilir.
        # Şimdilik sadece menüyü kapatırız.
        self.parent.parent.ids.nav_drawer.set_state("close")

    # Bu metot, menüdeki "Çıkış Yap" butonuna basıldığında çağrılır.
    def navigate_to_login(self):
        print("Çıkış yapılıyor, login ekranına dönülüyor.")
        sm = self.parent.parent.ids.screen_manager
        sm.current = 'login_screen'
        self.parent.parent.ids.nav_drawer.set_state("close")

    # Bu metot, MDTopAppBar'daki menü ikonuna basıldığında çağrılır.
    def toggle_navigation_drawer(self):
        """Menüyü açıp kapamak için kullanılır."""
        # MDNavigationLayout'a erişim için parent hiyerarşisini kullanıyoruz.
        nav_layout = self.parent.parent
        nav_drawer = nav_layout.ids.nav_drawer
        nav_drawer.set_state("open" if nav_drawer.state == "close" else "close")
