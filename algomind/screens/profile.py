"""
Profil Ekranı
=============

Bu modül, kullanıcının profil bilgilerini gösterir ve yönetir.
"""

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp

class ProfileEkrani(MDScreen):
    """
    Kullanıcı profili, ayarlar ve çıkış işlemlerini yöneten ekran.
    """

    def on_pre_enter(self, *args):
        """
        Ekran görüntülenmeden hemen önce çağrılır.
        Kullanıcı verilerini yüklemek ve arayüzü güncellemek için kullanılır.
        """
        self.load_user_data()
        super().on_pre_enter(*args)

    def load_user_data(self):
        """
        Ana uygulama sınıfından mevcut kullanıcı verilerini alır ve
        profil ekranındaki etiketleri günceller.
        """
        app = MDApp.get_running_app()
        # user_data'nın app sınıfında bir sözlük olarak tutulduğunu varsayıyoruz.
        user_data = getattr(app, 'user_data', None)

        if user_data and self.ids:
            # İsim ve soyisimi birleştirerek tam adı oluşturuyoruz.
            full_name = f"{user_data.get('name', '')} {user_data.get('surname', '')}"
            email = user_data.get('email', 'E-posta bilgisi yok')

            self.ids.name_label.text = full_name.strip()
            self.ids.email_label.text = email
        else:
            # Eğer veri bulunamazsa, varsayılan bir metin gösterilir.
            self.ids.name_label.text = "Kullanıcı Bilgisi Alınamadı"
            self.ids.email_label.text = "Lütfen tekrar giriş yapın."

    # Aşağıdaki fonksiyonlar, .kv dosyasında tanımlanan butonlar içindir.
    # Şimdilik sadece bir print ifadesi içeriyorlar.
    def edit_profile(self):
        """Profili düzenleme ekranına geçiş yapar (henüz uygulanmadı)."""
        print("Profili Düzenle butonuna basıldı.")

    def change_password(self):
        """Şifre değiştirme ekranına geçiş yapar (henüz uygulanmadı)."""
        print("Şifre Değiştir butonuna basıldı.")
