import random
import json
import threading  # Asenkron API çağrıları için
import time  # Gecikmeler için
import os  # Dosya işlemleri için

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock  # UI güncellemeleri ve zamanlayıcı için
from kivy.uix.image import Image  # Yerel resimler için AsyncImage yerine Image kullanıyoruz
from kivy.uix.popup import Popup  # Hata/bilgi mesajları için
from kivy.uix.progressbar import ProgressBar  # Yükleme göstergesi için

# requests kütüphanesi API çağrısı için gerekli
import requests

# Pencere boyutunu mobil görünüm için ayarlayalım
Window.size = (dp(360), dp(640))

# Gemini API Anahtarınızı buraya ekleyin (PyCharm için gerekli)
# Colab ortamında çalışıyorsanız boş bırakabilirsiniz, Canvas otomatik sağlar.
API_KEY = "AIzaSyAOec5mT-YcaRmZ6PviMGMOwJkC3CivIuI"  # Buraya kendi Gemini API anahtarınızı yapıştırın

# Besin listesi ve dosya adları (images klasöründeki dosyalar) - Güncellendi
FOOD_DATA = {
    "badem": ["badem.png"],
    "ceviz": ["ceviz.png"],
    "dondurma": ["dondurma.png"],
    "et": ["et.png"],
    "ekmek": ["ekmek.png"],
    "süt": ["süt.png"],
    "peynir": ["peynir.png"],
    "yumurta": ["yumurta.png"],
    "fındık": ["fındık.png"],
    "kurabiye": ["kurabiye.png"],
    "makarna": ["makarna.png"],
    "simit": ["simit.png"],
    "zeytin": ["zeytin.png"],
}


# --- Yardımcı Fonksiyonlar (Genel Buton Canvas Güncellemesi için) ---
def update_button_canvas(instance, value):
    """Butonların canvas elemanlarını (renk, dikdörtgen ve kenarlık) günceller."""
    # Kenarlık dikdörtgenini önce güncelle (varsa)
    if hasattr(instance, 'border_rect') and hasattr(instance, 'border_color'):
        border_width = dp(1.5)  # Kenarlık kalınlığı
        instance.border_rect.pos = (instance.pos[0] - border_width, instance.pos[1] - border_width)
        instance.border_rect.size = (instance.size[0] + 2 * border_width, instance.size[1] + 2 * border_width)
        instance.border_color.rgba = (1, 1, 1, 1)  # Beyaz kenarlık rengi

    # Ana buton dikdörtgenini güncelle
    instance.btn_rect.pos = instance.pos
    instance.btn_rect.size = instance.size
    instance.btn_color.rgba = instance.background_color


# --- Sayfa Sınıfları ---

# 1. Sayfa: LoginScreen (Kullanıcı Giriş Sayfası)
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.25, 0.45, 0.75, 1)  # Mavi tonu

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.main_layout.add_widget(
            Label(text='Giriş Yap', font_size='30sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(60)))
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.2))  # Boşluk

        self.username_input = TextInput(
            hint_text='Kullanıcı Adı',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size='18sp',
            padding_y=dp(10),
            background_color=(1, 1, 1, 0.8),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.main_layout.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text='Şifre',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(50),
            font_size='18sp',
            padding_y=dp(10),
            background_color=(1, 1, 1, 0.8),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.main_layout.add_widget(self.password_input)

        self.login_button = Button(
            text='Giriş Yap',
            size_hint_y=None,
            height=dp(60),
            font_size='22sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with self.login_button.canvas.before:
            self.login_button.btn_color = Color(*self.login_button.background_color)
            self.login_button.btn_rect = RoundedRectangle(pos=self.login_button.pos, size=self.login_button.size,
                                                          radius=[dp(15)] * 4)
            self.login_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.login_button.bind(on_press=self.do_login)
        self.main_layout.add_widget(self.login_button)

        self.message_label = Label(text='', color=(1, 0, 0, 1), font_size='16sp', size_hint_y=None, height=dp(30))
        self.main_layout.add_widget(self.message_label)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.5))  # Boşluk

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        """LoginScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color  # Screen'in background_color'ını kullan

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        # Basit frontend mantığı: Sadece ekran geçişi yapar
        if username == "admin" and password == "1234":
            self.message_label.text = "Giriş başarılı!"
            self.manager.get_screen('user_profile_screen').set_username(username)
            self.manager.current = 'user_profile_screen'
        else:
            self.message_label.text = "Kullanıcı adı veya şifre yanlış."


# 2. Sayfa: UserProfileScreen (Kullanıcının Adı ve Çıkış Yap)
class UserProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.25, 0.45, 0.75, 1)  # Mavi tonu

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.username_label = Label(text='Hoş Geldiniz, Kullanıcı!', font_size='28sp', color=(1, 1, 1, 1),
                                    size_hint_y=None, height=dp(60))
        self.main_layout.add_widget(self.username_label)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.3))  # Boşluk

        self.test_selection_button = Button(
            text='Testlere Başla',
            size_hint_y=None,
            height=dp(60),
            font_size='22sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with self.test_selection_button.canvas.before:
            self.test_selection_button.btn_color = Color(*self.test_selection_button.background_color)
            self.test_selection_button.btn_rect = RoundedRectangle(pos=self.test_selection_button.pos,
                                                                   size=self.test_selection_button.size,
                                                                   radius=[dp(15)] * 4)
            self.test_selection_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.test_selection_button.bind(on_press=self.go_to_test_selection)
        self.main_layout.add_widget(self.test_selection_button)

        self.logout_button = Button(
            text='Çıkış Yap',
            size_hint_y=None,
            height=dp(60),
            font_size='22sp',
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),  # Kırmızı tonu
            color=(1, 1, 1, 1)
        )
        with self.logout_button.canvas.before:
            self.logout_button.btn_color = Color(*self.logout_button.background_color)
            self.logout_button.btn_rect = RoundedRectangle(pos=self.logout_button.pos, size=self.logout_button.size,
                                                           radius=[dp(15)] * 4)
            self.logout_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.logout_button.bind(on_press=self.do_logout)
        self.main_layout.add_widget(self.logout_button)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.5))  # Boşluk

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        """UserProfileScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def set_username(self, username):
        self.username_label.text = f'Hoş Geldiniz, {username}!'

    def go_to_test_selection(self, instance):
        self.manager.current = 'test_selection_screen'

    def do_logout(self, instance):
        self.manager.current = 'login_screen'


# 3. Sayfa: TestSelectionScreen (Testlerimiz)
class TestSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.65, 0.35, 0.35, 1)  # Kırmızımsı/Kahverengimsi ton

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.main_layout.add_widget(
            Label(text='Testlerimiz', font_size='30sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(60)))
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.2))  # Boşluk

        # Besin Tanıma Testi Butonu - Güncellendi
        self.food_test_button = Button(
            text='Besin Tanıma Testi',
            size_hint_y=None,
            height=dp(60),
            font_size='22sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with self.food_test_button.canvas.before:
            self.food_test_button.btn_color = Color(*self.food_test_button.background_color)
            self.food_test_button.btn_rect = RoundedRectangle(pos=self.food_test_button.pos,
                                                                size=self.food_test_button.size, radius=[dp(15)] * 4)
            self.food_test_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.food_test_button.bind(on_press=self.start_food_test)
        self.main_layout.add_widget(self.food_test_button)

        # Diğer test butonları eklenebilir
        test_names = ["Renk  Testi", "Matematik Testi", "Hayvanlar Testi", "Meyve ve Sebzeler Testi", "Nesneler Testi"]
        for name in test_names:
            btn = Button(
                text=name,
                size_hint_y=None,
                height=dp(60),
                font_size='22sp',
                background_normal='',
                background_color=(0.25, 0.45, 0.75, 1),
                color=(1, 1, 1, 1)
            )
            with btn.canvas.before:
                btn.btn_color = Color(*btn.background_color)
                btn.btn_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(15)] * 4)
                btn.bind(pos=update_button_canvas, size=update_button_canvas)
            self.main_layout.add_widget(btn)

        self.main_layout.add_widget(BoxLayout(size_hint_y=0.5))  # Boşluk

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        """TestSelectionScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def start_food_test(self, instance): # Fonksiyon adı güncellendi
        # Öğrenci seçme ekranına geçiş yap
        self.manager.current = 'student_selection_screen'


# 4. Sayfa: StudentSelectionScreen (Öğrenci Seç)
class StudentSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        # Ekranın arka plan rengi
        self.background_color = (0.4, 0.6, 0.4, 1)  # Yeşilimsi ton (image_a42c29.png'ye göre)

        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        # Üst kısım: Geri butonu ve Profil butonu
        top_bar_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=(0, dp(5), 0, dp(5)),
            spacing=dp(10)
        )

        # Geri butonu
        back_button = Button(
            text='<',
            size_hint_x=None,
            width=dp(50),
            font_size='24sp',
            background_normal='',
            # Buton rengi ana ekranın arka plan rengiyle aynı
            background_color=self.background_color,
            color=(1, 1, 1, 1)  # Beyaz yazı
        )
        # Geri butonu için köşeleri yuvarlama ve çerçeve
        with back_button.canvas.before:
            # Beyaz çerçeve
            back_button.border_color = Color(1, 1, 1, 1)
            back_button.border_rect = RoundedRectangle(
                pos=(back_button.pos[0] - dp(1.5), back_button.pos[1] - dp(1.5)),
                size=(back_button.size[0] + dp(3), back_button.size[1] + dp(3)),
                radius=[dp(10) + dp(1.5)] * 4
            )
            # Ana buton rengi
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(
                pos=back_button.pos,
                size=back_button.size,
                radius=[dp(10)] * 4
            )
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)

        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))

        # Profil butonu (DEĞİŞTİRİLDİ: Arka plan mavi, çerçeve beyaz)
        profile_button = Button(
            text='Profil',
            size_hint_x=None,
            width=dp(100),
            font_size='18sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Mavi tonu
            color=(1, 1, 1, 1)  # Beyaz yazı
        )
        # Profil butonu için köşeleri yuvarlama ve çerçeve
        with profile_button.canvas.before:
            # Beyaz çerçeve
            profile_button.border_color = Color(1, 1, 1, 1)
            profile_button.border_rect = RoundedRectangle(
                pos=(profile_button.pos[0] - dp(1.5), profile_button.pos[1] - dp(1.5)),
                size=(profile_button.size[0] + dp(3), profile_button.size[1] + dp(3)),
                radius=[dp(10) + dp(1.5)] * 4
            )
            # Ana buton rengi
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(
                pos=profile_button.pos,
                size=profile_button.size,
                radius=[dp(10)] * 4
            )
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)

        self.main_layout.add_widget(top_bar_layout)

        # "Öğrenci Seçin" dropdown butonu
        self.main_dropdown_button = Button(
            text='Öğrenci Seçin',
            size_hint_y=None,
            height=dp(70),
            font_size='24sp',
            background_normal='',
            # Buton rengi ana ekranın arka plan rengiyle aynı
            background_color=self.background_color,
            color=(1, 1, 1, 1)
        )
        # Butonun köşelerini yuvarlamak ve çerçeve eklemek için canvas kullanın
        with self.main_dropdown_button.canvas.before:
            # Beyaz çerçeve
            self.main_dropdown_button.border_color = Color(1, 1, 1, 1)
            self.main_dropdown_button.border_rect = RoundedRectangle(
                pos=(self.main_dropdown_button.pos[0] - dp(1.5), self.main_dropdown_button.pos[1] - dp(1.5)),
                size=(self.main_dropdown_button.size[0] + dp(3), self.main_dropdown_button.size[1] + dp(3)),
                radius=[dp(15) + dp(1.5)] * 4
            )
            # Ana buton rengi
            self.main_dropdown_button.btn_color = Color(*self.main_dropdown_button.background_color)
            self.main_dropdown_button.btn_rect = RoundedRectangle(
                pos=self.main_dropdown_button.pos,
                size=self.main_dropdown_button.size,
                radius=[dp(15)] * 4
            )
            self.main_dropdown_button.bind(pos=update_button_canvas, size=update_button_canvas)

        self.main_layout.add_widget(self.main_dropdown_button)

        # Dropdown oluşturma
        self.dropdown = DropDown()

        # Öğrenci listesi
        self.ogrenci_listesi = ['Ali', 'Veli', 'Kasım', 'Zeynep']

        # Dropdown içeriği için bir ScrollView ve BoxLayout
        dropdown_height = (len(self.ogrenci_listesi) * dp(55)) + dp(10)
        scroll_view = ScrollView(size_hint_y=None, height=dropdown_height)

        dropdown_content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(5)
        )
        dropdown_content_layout.bind(minimum_height=dropdown_content_layout.setter('height'))

        # Dropdown kutusu için arka plan rengi ve yuvarlak köşeler (bu kısım değişmedi)
        with dropdown_content_layout.canvas.before:
            self.dropdown_content_layout_bg_color = Color(0.7, 0.6, 0.4, 1)  # Kahve tonu (görüntüye göre)
            self.dropdown_content_layout_bg_rect = RoundedRectangle(pos=dropdown_content_layout.pos,
                                                                    size=dropdown_content_layout.size,
                                                                    radius=[dp(10)] * 4)
            dropdown_content_layout.bind(pos=self._update_dropdown_layout_bg, size=self._update_dropdown_layout_bg)

        for ogrenci_adi in self.ogrenci_listesi:
            btn = Button(
                text=ogrenci_adi,
                size_hint_y=None,
                height=dp(50),
                font_size='20sp',
                background_normal='',
                # Buton rengi ana ekranın arka plan rengiyle aynı
                background_color=self.background_color,
                color=(1, 1, 1, 1)
            )
            # Dropdown elemanları için köşeleri yuvarlama ve çerçeve
            with btn.canvas.before:
                # Beyaz çerçeve
                btn.border_color = Color(1, 1, 1, 1)
                btn.border_rect = RoundedRectangle(
                    pos=(btn.pos[0] - dp(1.5), btn.pos[1] - dp(1.5)),
                    size=(btn.size[0] + dp(3), btn.size[1] + dp(3)),
                    radius=[dp(10) + dp(1.5)] * 4
                )
                # Ana buton rengi
                btn.btn_color = Color(*btn.background_color)
                btn.btn_rect = RoundedRectangle(
                    pos=btn.pos,
                    size=btn.size,
                    radius=[dp(10)] * 4
                )
                btn.bind(pos=update_button_canvas, size=update_button_canvas)

            btn.bind(on_release=lambda btn_instance, text=ogrenci_adi: self.select_ogrenci(btn_instance, text))
            dropdown_content_layout.add_widget(btn)

        scroll_view.add_widget(dropdown_content_layout)
        self.dropdown.add_widget(scroll_view)

        # Dropdown'ı ana butona bağla
        self.main_dropdown_button.bind(on_release=self.dropdown.open)

        self.selected_ogrenci_label = Label(
            text="Lütfen bir öğrenci seçin",
            size_hint_y=None,
            height=dp(50),
            font_size='22sp',
            color=(1, 1, 1, 1)  # Beyaz yazı
        )
        self.main_layout.add_widget(self.selected_ogrenci_label)

        self.start_test_button = Button(
            text='Testi Başlat',
            size_hint_y=None,
            height=dp(60),
            font_size='20sp',
            background_normal='',
            # Buton rengi ana ekranın arka plan rengiyle aynı
            background_color=self.background_color,
            color=(1, 1, 1, 1)
        )
        with self.start_test_button.canvas.before:
            # Beyaz çerçeve
            self.start_test_button.border_color = Color(1, 1, 1, 1)
            self.start_test_button.border_rect = RoundedRectangle(
                pos=(self.start_test_button.pos[0] - dp(1.5), self.start_test_button.pos[1] - dp(1.5)),
                size=(self.start_test_button.size[0] + dp(3), self.start_test_button.size[1] + dp(3)),
                radius=[dp(15) + dp(1.5)] * 4
            )
            # Ana buton rengi
            self.start_test_button.btn_color = Color(*self.start_test_button.background_color)
            self.start_test_button.btn_rect = RoundedRectangle(
                pos=self.start_test_button.pos,
                size=self.start_test_button.size,
                radius=[dp(15)] * 4
            )
            self.start_test_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.start_test_button.bind(on_press=self.go_to_test_questions)
        self.main_layout.add_widget(self.start_test_button)

        self.main_layout.add_widget(BoxLayout())  # Esnek boşluk

        # Son olarak, bu Screen'e ana layout'u ekle
        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        """StudentSelectionScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def _update_dropdown_layout_bg(self, instance, value):
        """StudentSelectionScreen'deki dropdown_content_layout'un arka planını günceller."""
        self.dropdown_content_layout_bg_rect.pos = instance.pos
        self.dropdown_content_layout_bg_rect.size = instance.size

    def on_back_button_press(self, instance):
        self.manager.current = 'test_selection_screen'  # Test seçim ekranına geri dön

    def on_profile_button_press(self, instance):
        self.manager.current = 'user_profile_screen'  # Kullanıcı profil ekranına geçiş

    def select_ogrenci(self, instance, ogrenci_adi):
        self.main_dropdown_button.text = f'Seçilen: {ogrenci_adi}'
        self.selected_ogrenci_label.text = f'Seçilen Öğrenci: {ogrenci_adi}'
        self.manager.selected_student = ogrenci_adi  # Seçilen öğrenciyi ScreenManager'da sakla
        self.dropdown.dismiss()

    def go_to_test_questions(self, instance):
        if self.manager.selected_student:
            self.manager.get_screen('test_questions_screen').start_test(self.manager.selected_student)
            self.manager.current = 'test_questions_screen'
        else:
            self.selected_ogrenci_label.text = "Lütfen bir öğrenci seçin!"
            self.selected_ogrenci_label.color = (1, 0, 0, 1)  # Kırmızı uyarı


# 5. Sayfa: TestQuestionsScreen (Test Soruları)
class TestQuestionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.25, 0.45, 0.75, 1)  # Mavi tonu

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        # Üst kısım: Geri butonu ve Profil butonu
        top_bar_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=(0, dp(5), 0, dp(5)),
            spacing=dp(10)
        )
        back_button = Button(
            text='<',
            size_hint_x=None,
            width=dp(50),
            font_size='24sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)

        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))

        self.timer_label = Label(text="00:00", font_size='20sp', color=(1, 1, 1, 1), size_hint_x=None, width=dp(80))
        top_bar_layout.add_widget(self.timer_label)

        profile_button = Button(
            text='Profil',
            size_hint_x=None,
            width=dp(100),
            font_size='18sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)

        self.main_layout.add_widget(top_bar_layout)

        # Soru numarası
        self.question_number_label = Label(text='Soru 1/10', font_size='24sp', color=(1, 1, 1, 1), size_hint_y=None,
                                           height=dp(50))
        self.main_layout.add_widget(self.question_number_label)

        # Resim (Besin) - Güncellendi
        self.food_image = Image(
            source='images/süt.png',  # Varsayılan resim
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            pos_hint={'center_x': 0.5}
        )
        self.main_layout.add_widget(self.food_image)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))  # Boşluk

        # Seçenek butonları
        self.option_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),
                                               spacing=dp(10))
        self.option1_button = Button(
            text='Seçenek 1',
            font_size='20sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with self.option1_button.canvas.before:
            self.option1_button.btn_color = Color(*self.option1_button.background_color)
            self.option1_button.btn_rect = RoundedRectangle(pos=self.option1_button.pos, size=self.option1_button.size,
                                                            radius=[dp(15)] * 4)
            self.option1_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option1_button.bind(on_press=lambda x: self.check_answer(self.option1_button.text))
        self.option_buttons_layout.add_widget(self.option1_button)

        self.option2_button = Button(
            text='Seçenek 2',
            font_size='20sp',
            background_normal='',
            background_color=(0.25, 0.45, 0.75, 1),  # Giriş sayfası renginde buton
            color=(1, 1, 1, 1)
        )
        with self.option2_button.canvas.before:
            self.option2_button.btn_color = Color(*self.option2_button.background_color)
            self.option2_button.btn_rect = RoundedRectangle(pos=self.option2_button.pos, size=self.option2_button.size,
                                                            radius=[dp(15)] * 4)
            self.option2_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option2_button.bind(on_press=lambda x: self.check_answer(self.option2_button.text))
        self.option_buttons_layout.add_widget(self.option2_button)

        self.main_layout.add_widget(self.option_buttons_layout)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))  # Boşluk

        self.test_finish_button = Button(
            text='Testi Bitir',
            size_hint_y=None,
            height=dp(60),
            font_size='20sp',
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),  # Kırmızı tonu
            color=(1, 1, 1, 1)
        )
        with self.test_finish_button.canvas.before:
            self.test_finish_button.btn_color = Color(*self.test_finish_button.background_color)
            self.test_finish_button.btn_rect = RoundedRectangle(pos=self.test_finish_button.pos,
                                                                size=self.test_finish_button.size, radius=[dp(15)] * 4)
            self.test_finish_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.test_finish_button.bind(on_press=self.finish_test)
        self.test_finish_button.disabled = True  # Başlangıçta devre dışı
        self.main_layout.add_widget(self.test_finish_button)

        self.main_layout.add_widget(BoxLayout())  # Esnek boşluk
        self.add_widget(self.main_layout)

        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.total_questions = 10  # Toplam soru sayısı 10 olarak belirlendi
        self.selected_student = None
        self.test_started = False
        self.timer_event = None
        self.time_elapsed = 0
        self.test_questions_data = []  # Besin sorularını burada saklayacağız - Güncellendi

        # Yükleme göstergesi
        self.loading_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(20),
            spacing=dp(10)
        )
        self.loading_layout.add_widget(Label(text="Sorular Hazırlanıyor...", font_size='20sp', color=(1, 1, 1, 1)))
        self.loading_progress = ProgressBar(max=100, value=0)
        self.loading_layout.add_widget(self.loading_progress)
        self.loading_popup = Popup(title='Yükleniyor', content=self.loading_layout,
                                   size_hint=(None, None), size=(dp(300), dp(200)),
                                   auto_dismiss=False)

    def _update_main_layout_bg(self, instance, value):
        """TestQuestionsScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def start_test(self, student_name):
        self.selected_student = student_name
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.time_elapsed = 0
        self.test_finish_button.disabled = True  # Sorular yüklenene kadar devre dışı
        self.test_started = False  # Test henüz başlamadı
        self.test_questions_data = []  # Önceki test verilerini temizle

        self.loading_popup.open()
        # Besin sorularını hazırla - Güncellendi
        threading.Thread(target=self._prepare_food_questions_thread).start()

    def _prepare_food_questions_thread(self): # Fonksiyon adı güncellendi
        """Besin sorularını hazırlayan thread.""" # Yorum güncellendi
        try:
            questions = self.prepare_food_questions() # Fonksiyon adı güncellendi
            if questions:
                # UI güncellemesini ana Kivy thread'inde yap
                Clock.schedule_once(lambda dt: self._on_questions_loaded(questions), 0)
            else:
                Clock.schedule_once(lambda dt: self._show_error_popup(
                    "Sorular hazırlanamadı. Images klasöründeki dosyaları kontrol edin."), 0)
        except Exception as e:
            print(f"Soru hazırlama hatası: {e}")
            Clock.schedule_once(lambda dt: self._show_error_popup(f"Bir hata oluştu: {e}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)  # Pop-up'ı kapat

    def prepare_food_questions(self): # Fonksiyon adı güncellendi
        """Images klasöründeki görselleri kullanarak besin tanıma soruları hazırlar.""" # Yorum güncellendi
        questions = []
        available_foods = list(FOOD_DATA.keys()) # Değişken adı güncellendi

        # Mevcut dosyaları kontrol et
        if not os.path.exists('../besinler_renkler/food_images'):
            print("Images klasörü bulunamadı!")
            return None

        # Besin listesini karıştır - Güncellendi
        random.shuffle(available_foods)

        for correct_food in available_foods[:10]:  # Her besinden 1 tane al, toplam 10 besin - Güncellendi
            food_images = FOOD_DATA[correct_food] # Değişken adı güncellendi
            selected_image = random.choice(food_images) # Değişken adı güncellendi
            image_path = f'images/{selected_image}'

            # Dosyanın var olup olmadığını kontrol et
            if not os.path.exists(image_path):
                print(f"Uyarı: {image_path} dosyası bulunamadı, atlanıyor...")
                continue

            # Yanlış seçenek için farklı bir besin seç - Güncellendi
            wrong_foods = [food for food in available_foods if food != correct_food] # Değişken adı güncellendi
            # Hata olasılığını azaltmak için, eğer yanlış besin yoksa (tek bir besin varsa listede), döngüyü kır
            if not wrong_foods:
                print(f"Uyarı: Yanlış seçenek oluşturulamıyor, sadece bir besin var: {correct_food}")
                break
            wrong_food = random.choice(wrong_foods) # Değişken adı güncellendi

            # Seçenekleri karıştır
            options = [correct_food, wrong_food] # Değişken adı güncellendi
            random.shuffle(options)

            question = {
                "image": image_path,
                "correct_answer": correct_food, # Değişken adı güncellendi
                "options": options
            }
            questions.append(question)

        # Eğer yeterli soru oluşturulamadıysa, eksik olanları tamamla
        while len(questions) < 10 and len(available_foods) >= 2: # En az 2 besin olmalı ki yanlış seçenek oluşturulabilsin
            # Rastgele bir besin seç - Güncellendi
            correct_food = random.choice(available_foods)
            food_images = FOOD_DATA[correct_food] # Değişken adı güncellendi
            selected_image = random.choice(food_images) # Değişken adı güncellendi
            image_path = f'../besinler_renkler/food_images/{selected_image}'

            # Yanlış seçenek için farklı bir besin seç - Güncellendi
            wrong_foods = [food for food in available_foods if food != correct_food] # Değişken adı güncellendi
            if not wrong_foods: # Tekrar kontrol
                break
            wrong_food = random.choice(wrong_foods) # Değişken adı güncellendi

            # Seçenekleri karıştır
            options = [correct_food, wrong_food] # Değişken adı güncellendi
            random.shuffle(options)

            question = {
                "image": image_path,
                "correct_answer": correct_food, # Değişken adı güncellendi
                "options": options
            }
            questions.append(question)

        return questions[:10]  # Sadece 10 soru döndür


    def _on_questions_loaded(self, questions):
        """Sorular hazırlandıktan sonra UI'ı günceller ve testi başlatır."""
        if not questions:
            self._show_error_popup("Sorular hazırlanamadı.")
            return

        self.test_questions_data = questions
        random.shuffle(self.test_questions_data)  # Soruları karıştır
        self.total_questions = len(self.test_questions_data)  # Toplam soru sayısını güncelle
        self.test_finish_button.disabled = False
        self.test_started = True
        self.load_question()
        self.start_timer()
        self.loading_popup.dismiss()  # Yükleme pop-up'ını kapat

    def _show_error_popup(self, message):
        """Kullanıcıya hata mesajı gösteren bir pop-up."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, color=(1, 0, 0, 1)))
        close_button = Button(text="Kapat", size_hint_y=None, height=dp(40))
        content.add_widget(close_button)
        popup = Popup(title="Hata", content=content, size_hint=(0.7, 0.3), auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()
        self.loading_popup.dismiss()  # Hata durumunda yükleme pop-up'ını kapat

    def start_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.timer_label.text = f"{minutes:02}:{seconds:02}"

    def load_question(self):
        if self.current_question_index < self.total_questions:
            question_data = self.test_questions_data[self.current_question_index]
            self.question_number_label.text = f'Soru {self.current_question_index + 1}/{self.total_questions}'

            # Resmi yükle
            try:
                self.food_image.source = question_data["image"] # Değişken adı güncellendi
            except Exception as e:
                print(f"Resim yükleme hatası: {e}")
                self.food_image.source = 'food_images/default.jpg'  # Varsayılan resim - Güncellendi

            # Seçenekleri ayarla
            options = question_data["options"]
            self.option1_button.text = options[0]
            self.option2_button.text = options[1]
            self.enable_options()
        else:
            self.finish_test()

    def check_answer(self, selected_option):
        question_data = self.test_questions_data[self.current_question_index]
        if selected_option == question_data["correct_answer"]:
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1
        self.disable_options()  # Seçenekleri devre dışı bırak

        # Kısa bir gecikme sonrası sonraki soruya geç
        Clock.schedule_once(self.next_question, 1)

    def next_question(self, dt):
        self.current_question_index += 1
        self.load_question()

    def enable_options(self):
        self.option1_button.disabled = False
        self.option2_button.disabled = False

    def disable_options(self):
        self.option1_button.disabled = True
        self.option2_button.disabled = True

    def finish_test(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
        self.test_started = False
        self.test_finish_button.disabled = True

        total_questions = self.total_questions
        correct = self.correct_answers
        incorrect = self.incorrect_answers
        empty = total_questions - (correct + incorrect)
        percentage = (correct / total_questions) * 100 if total_questions > 0 else 0

        report_data = {
            "ogrenci_adi": self.selected_student,
            "konu": "Besin Tanıma Testi", # Güncellendi
            "dogru_cevap": correct,
            "yanlis_cevap": incorrect,
            "bos_cevap": empty,
            "toplam_soru": total_questions,
            "yuzde": round(percentage, 2),
            "sure": self.time_elapsed
        }
        # Rapor ekranına geçiş yap ve verileri gönder
        self.manager.get_screen('report_screen').update_report(report_data)
        self.manager.current = 'report_screen'

    def on_back_button_press(self, instance):
        # Test devam ederken geri tuşuna basılırsa testi bitir
        if self.test_started:
            self.finish_test()
        else:
            self.manager.current = 'student_selection_screen'  # Öğrenci seçim ekranına geri dön

    def on_profile_button_press(self, instance):
        if self.test_started:
            self.finish_test()  # Test devam ederken profil butonuna basılırsa testi bitir
        self.manager.current = 'user_profile_screen'  # Kullanıcı profil ekranına geçiş


# 6. Sayfa: ReportScreen (Rapor Sayfası)
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        self.background_color = (0.7, 0.6, 0.4, 1)  # Kahve/bej tonu

        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        # Üst kısım: Geri butonu ve Profil butonu
        top_bar_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=(0, dp(5), 0, dp(5)),
            spacing=dp(10)
        )

        back_button = Button(
            text='<',
            size_hint_x=None,
            width=dp(50),
            font_size='24sp',
            background_normal='',
            background_color=(0.96, 0.87, 0.70, 1),  # TEN RENGİ
            color=(0, 0, 0, 1)  # Siyah yazı rengi
        )
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)

        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))

        profile_button = Button(
            text='Profil',
            size_hint_x=None,
            width=dp(100),
            font_size='18sp',
            background_normal='',
            background_color=(0.96, 0.87, 0.70, 1),  # TEN RENGİ
            color=(0, 0, 0, 1)  # Siyah yazı rengi
        )
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)

        self.main_layout.add_widget(top_bar_layout)

        self.report_title_label = Label(
            text='Rapor',
            font_size='26sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.main_layout.add_widget(self.report_title_label)

        self.report_scroll_view = ScrollView(size_hint_y=1)
        self.report_content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(15),  # Padding artırıldı
            spacing=dp(10)
        )
        self.report_content_layout.bind(minimum_height=self.report_content_layout.setter('height'))

        with self.report_content_layout.canvas.before:
            self.report_bg_color = Color(1, 1, 1, 1)  # Rapor kutusu beyaz arka plan
            self.report_bg_rect = RoundedRectangle(pos=self.report_content_layout.pos,
                                                   size=self.report_content_layout.size, radius=[dp(15)] * 4)
            self.report_content_layout.bind(pos=self._update_report_layout_canvas,
                                            size=self._update_report_layout_canvas)

        self.report_text_content = Label(
            text="Rapor Yükleniyor...",  # Başlangıçta yükleme mesajı
            color=(0, 0, 0, 1),
            font_size='18sp',
            size_hint_y=None,
            # Initial text_size can be set to (None, None) or a default, as it will be updated later.
            halign='left',
            valign='top',
            markup=True  # Markup desteği eklendi
        )
        self.report_text_content.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))


        # Bind the width of report_content_layout to update the label's text_size
        self.report_content_layout.bind(width=self._on_content_layout_width_change)


        self.report_content_layout.add_widget(self.report_text_content)
        self.report_scroll_view.add_widget(self.report_content_layout)
        self.main_layout.add_widget(self.report_scroll_view)

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        """ReportScreen'deki main_layout'un arka planını günceller."""
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def _update_report_layout_canvas(self, instance, value):
        self.report_bg_rect.pos = instance.pos
        self.report_bg_rect.size = instance.size

    def on_back_button_press(self, instance):
        self.manager.current = 'test_questions_screen'  # Test soruları ekranına geri dön

    def on_profile_button_press(self, instance):
        self.manager.current = 'user_profile_screen'  # Kullanıcı profil ekranına geçiş

    def update_report(self, report_data):
        """Rapor verilerini günceller ve Gemini API'den yorum alır."""
        self.report_text_content.text = "Gemini Yorumu Oluşturuluyor..."
        # Gemini API çağrısı ayrı bir thread'de yapılmalı
        threading.Thread(target=self._fetch_gemini_comment_thread, args=(report_data,)).start()

    def _fetch_gemini_comment_thread(self, report_data):
        """Senkron olarak Gemini API'den yorum alır (Kivy main thread'inden çağrılmak üzere)."""
        prompt = f"""
        Aşağıdaki öğrenci test sonuçlarına göre detaylı bir rapor ve yorum oluştur:
        Öğrenci Adı: {report_data['ogrenci_adi']}
        Konu: {report_data['konu']}
        Toplam Soru: {report_data['toplam_soru']}
        Doğru Cevap: {report_data['dogru_cevap']}
        Yanlış Cevap: {report_data['yanlis_cevap']}
        Boş Cevap: {report_data['bos_cevap']}
        Başarı Yüzdesi: %{report_data['yuzde']}
        Test Süresi: {report_data['sure']} saniye

        Bu besin tanıma testi sonuçlarına göre öğrencinin: # Güncellendi
        - Görsel algı ve tanıma becerilerini değerlendir
        - Besinler hakkındaki genel bilgi düzeyini yorumla # Güncellendi
        - Konsantrasyon ve dikkat süresini analiz et
        - Gelişim alanlarını belirt ve öneriler sun
        - Motivasyonunu artıracak pozitif bir dil kullan
        """

        try:
            chatHistory = []
            chatHistory.append({"role": "user", "parts": [{"text": prompt}]})
            payload = {"contents": chatHistory}
            apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

            retries = 3
            for i in range(retries):
                try:
                    response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
                    response.raise_for_status()  # HTTP hataları için

                    result = response.json()
                    gemini_comment = "Yorum alınamadı."
                    if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0][
                        'content'].get('parts'):
                        gemini_comment = result['candidates'][0]['content']['parts'][0]['text']

                    # Ana Kivy thread'inde UI güncellemesi yap
                    Clock.schedule_once(lambda dt: self._update_report_ui(report_data, gemini_comment))
                    return  # Başarılı olursa döngüden çık
                except requests.exceptions.RequestException as e:
                    print(f"API isteği hatası (Deneme {i + 1}/{retries}): {e}")
                    if i < retries - 1:
                        time.sleep(2 ** i)  # Üstel geri çekilme
                    else:
                        Clock.schedule_once(lambda dt: self._update_report_ui(report_data,
                                                                              "Rapor yorumu alınırken bir hata oluştu: Ağ bağlantısı sorunu."),
                                            0)
                        return
                except Exception as e:
                    print(f"Beklenmeyen hata: {e}")
                    Clock.schedule_once(
                        lambda dt: self._update_report_ui(report_data, f"Rapor yorumu alınırken bir hata oluştu: {e}"),
                        0)
                    return

        except Exception as e:
            print(f"Gemini API hatası: {e}")
            Clock.schedule_once(
                lambda dt: self._update_report_ui(report_data, "Rapor yorumu alınırken bir hata oluştu."), 0)

    def _update_report_ui(self, report_data, gemini_comment):
        """Rapor UI'ını günceller."""
        report_text = f"""
[b]Öğrenci:[/b] {report_data.get('ogrenci_adi', 'Bilinmiyor')}
[b]Konu:[/b] {report_data.get('konu', 'Bilinmiyor')}
[b]Toplam Soru:[/b] {report_data.get('toplam_soru', 0)}
[b]Doğru:[/b] {report_data.get('dogru_cevap', 0)}
[b]Yanlış:[/b] {report_data.get('yanlis_cevap', 0)}
[b]Boş:[/b] {report_data.get('bos_cevap', 0)}
[b]Başarı Yüzdesi:[/b] %{report_data.get('yuzde', 0.0)}
[b]Süre:[/b] {report_data.get('sure', 0)} saniye

[b]Gemini Yorumu:[/b]
{gemini_comment}
"""
        self.report_text_content.text = report_text.strip()

        # Schedule the update of text_size and height to ensure layout has settled
        Clock.schedule_once(self._post_text_update_layout, 0.1) # A small delay



    def _post_text_update_layout(self, dt):
        """Ensures the text_size and height of report_text_content are correct after text update."""
        # Calculate the available width for the text within its parent (report_content_layout)
        available_width_for_text = self.report_content_layout.width - (dp(15) * 2) # report_content_layout has padding dp(15)

        # Ensure a minimum width to avoid division by zero or negative width
        if available_width_for_text <= 0:
            available_width_for_text = dp(1) # Small positive width

        self.report_text_content.text_size = (available_width_for_text, None)
        self.report_text_content.texture_update()
        self.report_text_content.height = self.report_text_content.texture_size[1]

    def _on_content_layout_width_change(self, instance, width):
        """Called when the width of report_content_layout changes."""
        # Recalculate available width for the label and update text_size
        available_width_for_text = width - (dp(15) * 2)
        if available_width_for_text <= 0:
            available_width_for_text = dp(1)
        self.report_text_content.text_size = (available_width_for_text, None)



# Ana Uygulama Sınıfı
class MobilEgitimApp(App):
    def build(self):  # build metodu artık async değil
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.selected_student = None  # Seçilen öğrenciyi saklamak için

        # 1. Login Ekranı
        self.sm.add_widget(LoginScreen(name='login_screen'))

        # 2. Kullanıcı Profil Ekranı
        self.sm.add_widget(UserProfileScreen(name='user_profile_screen'))

        # 3. Test Seçim Ekranı
        self.sm.add_widget(TestSelectionScreen(name='test_selection_screen'))

        # 4. Öğrenci Seçim Ekranı
        self.sm.add_widget(StudentSelectionScreen(name='student_selection_screen'))

        # 5. Test Soruları Ekranı
        self.sm.add_widget(TestQuestionsScreen(name='test_questions_screen'))

        # 6. Rapor Ekranı
        self.sm.add_widget(ReportScreen(name='report_screen'))

        return self.sm


if __name__ == '__main__':
    MobilEgitimApp().run()