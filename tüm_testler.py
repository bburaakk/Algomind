import random
import json
import threading
import time
import os

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
from kivy.clock import Clock
from kivy.uix.image import Image, AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

import requests

# Pencere boyutunu mobil görünüm için ayarlayalım
Window.size = (dp(360), dp(640))

# Gemini API Anahtarınızı buraya ekleyin
API_KEY = "AIzaSyAOec5mT-YcaRmZ6PviMGMOwJkC3CivIuI"  # Kendi Gemini API anahtarınızı buraya yapıştırın

# --- Veri Setleri ---

# Hayvan listesi ve dosya adları
ANIMAL_DATA = {
    "kedi": ["kedi.png"], "köpek": ["köpek.png"], "kuş": ["kuş.png"], "balık": ["balık.png"],
    "at": ["at.png"], "inek": ["inek.png"], "tavşan": ["tavşan.png"], "aslan": ["aslan.png"],
    "ayı": ["ayı.png"], "koyun": ["koyun.png"], "kurbağa": ["kurbağa.png"], "maymun": ["maymun.png"],
    "tavuk": ["tavuk.png"], "arı": ["arı.png"],
}

# Besin listesi ve dosya adları
FOOD_DATA = {
    "badem": ["badem.png"], "ceviz": ["ceviz.png"], "dondurma": ["dondurma.png"], "et": ["et.png"],
    "ekmek": ["ekmek.png"], "süt": ["süt.png"], "peynir": ["peynir.png"], "yumurta": ["yumurta.png"],
    "fındık": ["fındık.png"], "kurabiye": ["kurabiye.png"], "makarna": ["makarna.png"], "simit": ["simit.png"],
    "zeytin": ["zeytin.png"],
}

# Nesne listesi ve dosya adları
OBJECT_DATA = {
    "araba": ["araba.png"], "balon": ["balon.png"], "ev": ["ev.png"], "kalem": ["kalem.png"],
    "kapı": ["kapı.png"], "kitap": ["kitap.png"], "kitaplık": ["kitaplık.png"], "masa": ["masa.png"],
    "pencere": ["pencere.png"], "sandalye": ["sandalye.png"], "televizyon": ["televizyon.png"],
    "yapboz": ["yapboz.png"], "yatak": ["yatak.png"],
}

# Meyve ve sebze listesi ve dosya adları
MEYVE_SEBZE_DATA = {
    "armut": ["armut.png"], "domates": ["domates.png"], "elma": ["elma.png"], "havuç": ["havuç.png"],
    "karpuz": ["karpuz.png"], "kiraz": ["kiraz.png"], "limon": ["limon.png"], "muz": ["muz.png"],
    "patates": ["patates.png"], "portakal": ["portakal.png"], "salatalık": ["salatalık.png"],
    "çilek": ["çilek.png"], "şeftali": ["şeftali.png"], "üzüm": ["üzüm.png"],
}

# Renkler için yerel resim yolları
COLOR_IMAGE_MAP = {
    "kırmızı": "color_images/red.png", "mavi": "color_images/blue.png", "yeşil": "color_images/green.png",
    "sarı": "color_images/yellow.png", "mor": "color_images/purple.png", "turuncu": "color_images/orange.png",
    "siyah": "color_images/black.png", "beyaz": "color_images/white.png", "pembe": "color_images/pink.png",
    "kahverengi": "color_images/brown.png", "gri": "color_images/grey.png",
}


# --- Yardımcı Fonksiyonlar ---
def update_button_canvas(instance, value):
    """Butonların canvas elemanlarını (renk, dikdörtgen ve kenarlık) günceller."""
    if hasattr(instance, 'border_rect') and hasattr(instance, 'border_color'):
        border_width = dp(1.5)
        instance.border_rect.pos = (instance.pos[0] - border_width, instance.pos[1] - border_width)
        instance.border_rect.size = (instance.size[0] + 2 * border_width, instance.size[1] + 2 * border_width)
        instance.border_color.rgba = (1, 1, 1, 1)

    instance.btn_rect.pos = instance.pos
    instance.btn_rect.size = instance.size
    instance.btn_color.rgba = instance.background_color


# --- Sayfa Sınıfları ---

# 1. Sayfa: LoginScreen (Kullanıcı Giriş Sayfası) - Ortak
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.25, 0.45, 0.75, 1)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.main_layout.add_widget(
            Label(text='Giriş Yap', font_size='30sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(60)))
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.2))

        self.username_input = TextInput(
            hint_text='Kullanıcı Adı', multiline=False, size_hint_y=None, height=dp(50), font_size='18sp',
            padding_y=dp(10), background_color=(1, 1, 1, 0.8), foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.main_layout.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text='Şifre', multiline=False, password=True, size_hint_y=None, height=dp(50), font_size='18sp',
            padding_y=dp(10), background_color=(1, 1, 1, 0.8), foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.main_layout.add_widget(self.password_input)

        self.login_button = Button(
            text='Giriş Yap', size_hint_y=None, height=dp(60), font_size='22sp', background_normal='',
            background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1)
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
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.5))

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if username == "admin" and password == "1234":
            self.message_label.text = "Giriş başarılı!"
            self.manager.get_screen('user_profile_screen').set_username(username)
            self.manager.current = 'user_profile_screen'
        else:
            self.message_label.text = "Kullanıcı adı veya şifre yanlış."


# 2. Sayfa: UserProfileScreen (Kullanıcı Profili) - Ortak
class UserProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.25, 0.45, 0.75, 1)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.username_label = Label(text='Hoş Geldiniz, Kullanıcı!', font_size='28sp', color=(1, 1, 1, 1),
                                    size_hint_y=None, height=dp(60))
        self.main_layout.add_widget(self.username_label)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.3))

        self.test_selection_button = Button(
            text='Testlere Başla', size_hint_y=None, height=dp(60), font_size='22sp', background_normal='',
            background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1)
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
            text='Çıkış Yap', size_hint_y=None, height=dp(60), font_size='22sp', background_normal='',
            background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1)
        )
        with self.logout_button.canvas.before:
            self.logout_button.btn_color = Color(*self.logout_button.background_color)
            self.logout_button.btn_rect = RoundedRectangle(pos=self.logout_button.pos, size=self.logout_button.size,
                                                           radius=[dp(15)] * 4)
            self.logout_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.logout_button.bind(on_press=self.do_logout)
        self.main_layout.add_widget(self.logout_button)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.5))

        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def set_username(self, username):
        self.username_label.text = f'Hoş Geldiniz, {username}!'

    def go_to_test_selection(self, instance):
        self.manager.current = 'test_selection_screen'

    def do_logout(self, instance):
        self.manager.current = 'login_screen'


# 3. Sayfa: TestSelectionScreen (Test Seçimi) - Birleştirilmiş
class TestSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.65, 0.35, 0.35, 1)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(10))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        self.main_layout.add_widget(
            Label(text='Testlerimiz', font_size='30sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(60)))
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        test_list = {
            "animal": "Hayvan Tanıma Testi",
            "food": "Besin Tanıma Testi",
            "math": "Matematik Testi",
            "object": "Nesne Tanıma Testi",
            "fruit_vegetable": "Meyve Sebze Tanıma Testi",
            "color": "Renk Tanıma Testi"
        }

        for test_type, test_name in test_list.items():
            btn = Button(
                text=test_name, size_hint_y=None, height=dp(60), font_size='22sp',
                background_normal='', background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1)
            )
            with btn.canvas.before:
                btn.btn_color = Color(*btn.background_color)
                btn.btn_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(15)] * 4)
                btn.bind(pos=update_button_canvas, size=update_button_canvas)
            btn.bind(on_press=lambda instance, t_type=test_type: self.start_test(t_type))
            self.main_layout.add_widget(btn)

        self.main_layout.add_widget(BoxLayout(size_hint_y=0.2))
        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def start_test(self, test_type):
        self.manager.current_test_type = test_type
        self.manager.current = 'student_selection_screen'


# 4. Sayfa: StudentSelectionScreen (Öğrenci Seçimi) - Ortak
class StudentSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.background_color = (0.4, 0.6, 0.4, 1)

        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        top_bar_layout = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(50), padding=(0, dp(5), 0, dp(5)), spacing=dp(10)
        )

        back_button = Button(
            text='<', size_hint_x=None, width=dp(50), font_size='24sp', background_normal='',
            background_color=self.background_color, color=(1, 1, 1, 1)
        )
        with back_button.canvas.before:
            back_button.border_color = Color(1, 1, 1, 1)
            back_button.border_rect = RoundedRectangle(pos=(back_button.pos[0] - dp(1.5), back_button.pos[1] - dp(1.5)),
                                                       size=(back_button.size[0] + dp(3), back_button.size[1] + dp(3)),
                                                       radius=[dp(10) + dp(1.5)] * 4)
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)

        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))

        profile_button = Button(
            text='Profil', size_hint_x=None, width=dp(100), font_size='18sp', background_normal='',
            background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1)
        )
        with profile_button.canvas.before:
            profile_button.border_color = Color(1, 1, 1, 1)
            profile_button.border_rect = RoundedRectangle(
                pos=(profile_button.pos[0] - dp(1.5), profile_button.pos[1] - dp(1.5)),
                size=(profile_button.size[0] + dp(3), profile_button.size[1] + dp(3)),
                radius=[dp(10) + dp(1.5)] * 4)
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)

        self.main_layout.add_widget(top_bar_layout)

        self.main_dropdown_button = Button(
            text='Öğrenci Seçin', size_hint_y=None, height=dp(70), font_size='24sp', background_normal='',
            background_color=self.background_color, color=(1, 1, 1, 1)
        )
        with self.main_dropdown_button.canvas.before:
            self.main_dropdown_button.border_color = Color(1, 1, 1, 1)
            self.main_dropdown_button.border_rect = RoundedRectangle(
                pos=(self.main_dropdown_button.pos[0] - dp(1.5), self.main_dropdown_button.pos[1] - dp(1.5)),
                size=(self.main_dropdown_button.size[0] + dp(3), self.main_dropdown_button.size[1] + dp(3)),
                radius=[dp(15) + dp(1.5)] * 4)
            self.main_dropdown_button.btn_color = Color(*self.main_dropdown_button.background_color)
            self.main_dropdown_button.btn_rect = RoundedRectangle(pos=self.main_dropdown_button.pos,
                                                                  size=self.main_dropdown_button.size,
                                                                  radius=[dp(15)] * 4)
            self.main_dropdown_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.main_layout.add_widget(self.main_dropdown_button)

        self.dropdown = DropDown()
        self.ogrenci_listesi = ['Ali', 'Veli', 'Kasım', 'Zeynep']
        dropdown_height = (len(self.ogrenci_listesi) * dp(55)) + dp(10)
        scroll_view = ScrollView(size_hint_y=None, height=dropdown_height)
        dropdown_content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5), padding=dp(5))
        dropdown_content_layout.bind(minimum_height=dropdown_content_layout.setter('height'))
        with dropdown_content_layout.canvas.before:
            self.dropdown_content_layout_bg_color = Color(0.7, 0.6, 0.4, 1)
            self.dropdown_content_layout_bg_rect = RoundedRectangle(pos=dropdown_content_layout.pos,
                                                                    size=dropdown_content_layout.size,
                                                                    radius=[dp(10)] * 4)
            dropdown_content_layout.bind(pos=self._update_dropdown_layout_bg, size=self._update_dropdown_layout_bg)

        for ogrenci_adi in self.ogrenci_listesi:
            btn = Button(
                text=ogrenci_adi, size_hint_y=None, height=dp(50), font_size='20sp', background_normal='',
                background_color=self.background_color, color=(1, 1, 1, 1)
            )
            with btn.canvas.before:
                btn.border_color = Color(1, 1, 1, 1)
                btn.border_rect = RoundedRectangle(pos=(btn.pos[0] - dp(1.5), btn.pos[1] - dp(1.5)),
                                                   size=(btn.size[0] + dp(3), btn.size[1] + dp(3)),
                                                   radius=[dp(10) + dp(1.5)] * 4)
                btn.btn_color = Color(*btn.background_color)
                btn.btn_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(10)] * 4)
                btn.bind(pos=update_button_canvas, size=update_button_canvas)
            btn.bind(on_release=lambda btn_instance, text=ogrenci_adi: self.select_ogrenci(btn_instance, text))
            dropdown_content_layout.add_widget(btn)

        scroll_view.add_widget(dropdown_content_layout)
        self.dropdown.add_widget(scroll_view)
        self.main_dropdown_button.bind(on_release=self.dropdown.open)

        self.selected_ogrenci_label = Label(text="Lütfen bir öğrenci seçin", size_hint_y=None, height=dp(50),
                                            font_size='22sp', color=(1, 1, 1, 1))
        self.main_layout.add_widget(self.selected_ogrenci_label)

        self.start_test_button = Button(
            text='Testi Başlat', size_hint_y=None, height=dp(60), font_size='20sp', background_normal='',
            background_color=self.background_color, color=(1, 1, 1, 1)
        )
        with self.start_test_button.canvas.before:
            self.start_test_button.border_color = Color(1, 1, 1, 1)
            self.start_test_button.border_rect = RoundedRectangle(
                pos=(self.start_test_button.pos[0] - dp(1.5), self.start_test_button.pos[1] - dp(1.5)),
                size=(self.start_test_button.size[0] + dp(3), self.start_test_button.size[1] + dp(3)),
                radius=[dp(15) + dp(1.5)] * 4)
            self.start_test_button.btn_color = Color(*self.start_test_button.background_color)
            self.start_test_button.btn_rect = RoundedRectangle(pos=self.start_test_button.pos,
                                                               size=self.start_test_button.size, radius=[dp(15)] * 4)
            self.start_test_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.start_test_button.bind(on_press=self.go_to_test_questions)
        self.main_layout.add_widget(self.start_test_button)

        self.main_layout.add_widget(BoxLayout())
        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def _update_dropdown_layout_bg(self, instance, value):
        self.dropdown_content_layout_bg_rect.pos = instance.pos
        self.dropdown_content_layout_bg_rect.size = instance.size

    def on_back_button_press(self, instance):
        self.manager.current = 'test_selection_screen'

    def on_profile_button_press(self, instance):
        self.manager.current = 'user_profile_screen'

    def select_ogrenci(self, instance, ogrenci_adi):
        self.main_dropdown_button.text = f'Seçilen: {ogrenci_adi}'
        self.selected_ogrenci_label.text = f'Seçilen Öğrenci: {ogrenci_adi}'
        self.manager.selected_student = ogrenci_adi
        self.dropdown.dismiss()

    def go_to_test_questions(self, instance):
        if self.manager.selected_student:
            test_screen_name = self.manager.current_test_type + '_test_screen'
            self.manager.get_screen(test_screen_name).start_test(self.manager.selected_student)
            self.manager.current = test_screen_name
        else:
            self.selected_ogrenci_label.text = "Lütfen bir öğrenci seçin!"
            self.selected_ogrenci_label.color = (1, 0, 0, 1)


# Base class for image-based tests to reduce code duplication
class BaseImageTestScreen(Screen):
    def __init__(self, test_konu, data_dict, image_folder, **kwargs):
        super().__init__(**kwargs)
        self.test_konu = test_konu
        self.data_dict = data_dict
        self.image_folder = image_folder

        self.background_color = (0.25, 0.45, 0.75, 1)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        # Common widgets
        top_bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50),
                                   padding=(0, dp(5), 0, dp(5)), spacing=dp(10))
        back_button = Button(text='<', size_hint_x=None, width=dp(50), font_size='24sp', background_normal='',
                             background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)
        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))
        self.timer_label = Label(text="00:00", font_size='20sp', color=(1, 1, 1, 1), size_hint_x=None, width=dp(80))
        top_bar_layout.add_widget(self.timer_label)
        profile_button = Button(text='Profil', size_hint_x=None, width=dp(100), font_size='18sp', background_normal='',
                                background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)
        self.main_layout.add_widget(top_bar_layout)

        self.question_number_label = Label(text='Soru 1/10', font_size='24sp', color=(1, 1, 1, 1), size_hint_y=None,
                                           height=dp(50))
        self.main_layout.add_widget(self.question_number_label)

        self.item_image = Image(size_hint=(None, None), size=(dp(150), dp(150)), pos_hint={'center_x': 0.5})
        self.main_layout.add_widget(self.item_image)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.option_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),
                                               spacing=dp(10))
        self.option1_button = Button(text='Seçenek 1', font_size='20sp', background_normal='',
                                     background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with self.option1_button.canvas.before:
            self.option1_button.btn_color = Color(*self.option1_button.background_color)
            self.option1_button.btn_rect = RoundedRectangle(pos=self.option1_button.pos, size=self.option1_button.size,
                                                            radius=[dp(15)] * 4)
            self.option1_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option1_button.bind(on_press=lambda x: self.check_answer(self.option1_button.text))
        self.option_buttons_layout.add_widget(self.option1_button)

        self.option2_button = Button(text='Seçenek 2', font_size='20sp', background_normal='',
                                     background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with self.option2_button.canvas.before:
            self.option2_button.btn_color = Color(*self.option2_button.background_color)
            self.option2_button.btn_rect = RoundedRectangle(pos=self.option2_button.pos, size=self.option2_button.size,
                                                            radius=[dp(15)] * 4)
            self.option2_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option2_button.bind(on_press=lambda x: self.check_answer(self.option2_button.text))
        self.option_buttons_layout.add_widget(self.option2_button)
        self.main_layout.add_widget(self.option_buttons_layout)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.test_finish_button = Button(text='Testi Bitir', size_hint_y=None, height=dp(60), font_size='20sp',
                                         background_normal='', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        with self.test_finish_button.canvas.before:
            self.test_finish_button.btn_color = Color(*self.test_finish_button.background_color)
            self.test_finish_button.btn_rect = RoundedRectangle(pos=self.test_finish_button.pos,
                                                                size=self.test_finish_button.size, radius=[dp(15)] * 4)
            self.test_finish_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.test_finish_button.bind(on_press=self.finish_test)
        self.test_finish_button.disabled = True
        self.main_layout.add_widget(self.test_finish_button)

        self.main_layout.add_widget(BoxLayout())
        self.add_widget(self.main_layout)

        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.total_questions = 10
        self.selected_student = None
        self.test_started = False
        self.timer_event = None
        self.time_elapsed = 0
        self.test_questions_data = []

        self.loading_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.4),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5}, padding=dp(20), spacing=dp(10))
        self.loading_layout.add_widget(Label(text="Sorular Hazırlanıyor...", font_size='20sp', color=(1, 1, 1, 1)))
        self.loading_progress = ProgressBar(max=100, value=0)
        self.loading_layout.add_widget(self.loading_progress)
        self.loading_popup = Popup(title='Yükleniyor', content=self.loading_layout, size_hint=(None, None),
                                   size=(dp(300), dp(200)), auto_dismiss=False)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def start_test(self, student_name):
        self.selected_student = student_name
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.time_elapsed = 0
        self.test_finish_button.disabled = True
        self.test_started = False
        self.test_questions_data = []
        self.loading_popup.open()
        threading.Thread(target=self._prepare_questions_thread).start()

    def _prepare_questions_thread(self):
        try:
            questions = self.prepare_questions()
            if questions:
                Clock.schedule_once(lambda dt: self._on_questions_loaded(questions), 0)
            else:
                Clock.schedule_once(lambda dt: self._show_error_popup(
                    f"Sorular hazırlanamadı. '{self.image_folder}' klasörünü kontrol edin."), 0)
        except Exception as e:
            print(f"Soru hazırlama hatası: {e}")
            Clock.schedule_once(lambda dt: self._show_error_popup(f"Bir hata oluştu: {e}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)

    def prepare_questions(self):
        questions = []
        available_items = list(self.data_dict.keys())
        if not os.path.exists(self.image_folder):
            print(f"'{self.image_folder}' klasörü bulunamadı!")
            return None
        random.shuffle(available_items)

        generated_questions = 0
        while generated_questions < self.total_questions and len(available_items) > 1:
            correct_item = random.choice(available_items)
            item_images = self.data_dict[correct_item]
            selected_image = random.choice(item_images)
            image_path = os.path.join(self.image_folder, selected_image)

            if not os.path.exists(image_path):
                print(f"Uyarı: {image_path} dosyası bulunamadı, atlanıyor...")
                continue

            wrong_items = [item for item in available_items if item != correct_item]
            if not wrong_items:
                continue
            wrong_item = random.choice(wrong_items)
            options = [correct_item, wrong_item]
            random.shuffle(options)
            question = {"image": image_path, "correct_answer": correct_item, "options": options}
            questions.append(question)
            generated_questions += 1
        return questions

    def _on_questions_loaded(self, questions):
        if not questions:
            self._show_error_popup("Sorular hazırlanamadı.")
            return
        self.test_questions_data = questions
        random.shuffle(self.test_questions_data)
        self.total_questions = len(self.test_questions_data)
        self.test_finish_button.disabled = False
        self.test_started = True
        self.load_question()
        self.start_timer()
        self.loading_popup.dismiss()

    def _show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, color=(1, 0, 0, 1)))
        close_button = Button(text="Kapat", size_hint_y=None, height=dp(40))
        content.add_widget(close_button)
        popup = Popup(title="Hata", content=content, size_hint=(0.7, 0.3), auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()
        self.loading_popup.dismiss()

    def start_timer(self):
        if self.timer_event: self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_elapsed += 1
        minutes, seconds = divmod(self.time_elapsed, 60)
        self.timer_label.text = f"{minutes:02}:{seconds:02}"

    def load_question(self):
        if self.current_question_index < self.total_questions:
            question_data = self.test_questions_data[self.current_question_index]
            self.question_number_label.text = f'Soru {self.current_question_index + 1}/{self.total_questions}'
            try:
                self.item_image.source = question_data["image"]
            except Exception as e:
                print(f"Resim yükleme hatası: {e}")
                self.item_image.source = ''  # Varsayılan resim
            options = question_data["options"]
            self.option1_button.text = options[0]
            self.option2_button.text = options[1]
            self.enable_options()
        else:
            self.finish_test()

    def check_answer(self, selected_option):
        # DÜZELTME: `IndexError` hatasını önlemek için listeye erişmeden önce kontrol eklendi.
        if not self.test_questions_data or self.current_question_index >= len(self.test_questions_data):
            self.finish_test()
            return
        question_data = self.test_questions_data[self.current_question_index]
        if selected_option == question_data["correct_answer"]:
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1
        self.disable_options()
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
        if self.timer_event: self.timer_event.cancel()
        self.test_started = False
        self.test_finish_button.disabled = True

        total_questions = self.total_questions
        correct = self.correct_answers
        incorrect = self.incorrect_answers
        empty = total_questions - (correct + incorrect)
        percentage = (correct / total_questions) * 100 if total_questions > 0 else 0

        report_data = {
            "ogrenci_adi": self.selected_student, "konu": self.test_konu, "dogru_cevap": correct,
            "yanlis_cevap": incorrect, "bos_cevap": empty, "toplam_soru": total_questions,
            "yuzde": round(percentage, 2), "sure": self.time_elapsed
        }
        self.manager.get_screen('report_screen').update_report(report_data)
        self.manager.current = 'report_screen'

    def on_back_button_press(self, instance):
        if self.test_started:
            self.finish_test()
        else:
            self.manager.current = 'student_selection_screen'

    def on_profile_button_press(self, instance):
        if self.test_started: self.finish_test()
        self.manager.current = 'user_profile_screen'


# 5. Sayfalar: Her test için ayrı ekran sınıfları
class AnimalTestScreen(BaseImageTestScreen):
    def __init__(self, **kwargs):
        super().__init__(test_konu="Hayvan Tanıma Testi", data_dict=ANIMAL_DATA, image_folder="hayvanlar_images", **kwargs)


class FoodTestScreen(BaseImageTestScreen):
    def __init__(self, **kwargs):
        super().__init__(test_konu="Besin Tanıma Testi", data_dict=FOOD_DATA, image_folder="food_images", **kwargs)


class ObjectTestScreen(BaseImageTestScreen):
    def __init__(self, **kwargs):
        super().__init__(test_konu="Nesne Tanıma Testi", data_dict=OBJECT_DATA, image_folder="objects_images", **kwargs)


class FruitVegetableTestScreen(BaseImageTestScreen):
    def __init__(self, **kwargs):
        super().__init__(test_konu="Meyve Sebze Tanıma Testi", data_dict=MEYVE_SEBZE_DATA,
                         image_folder="meyve_sebze_images", **kwargs)


class ColorTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Color test has a different structure (Gemini-based questions), so it's not based on BaseImageTestScreen
        self.test_konu = "Renk Tanıma Testi"
        self.background_color = (0.25, 0.45, 0.75, 1)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        # Copied from BaseImageTestScreen and adapted
        top_bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50),
                                   padding=(0, dp(5), 0, dp(5)), spacing=dp(10))
        back_button = Button(text='<', size_hint_x=None, width=dp(50), font_size='24sp', background_normal='',
                             background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)
        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))
        self.timer_label = Label(text="00:00", font_size='20sp', color=(1, 1, 1, 1), size_hint_x=None, width=dp(80))
        top_bar_layout.add_widget(self.timer_label)
        profile_button = Button(text='Profil', size_hint_x=None, width=dp(100), font_size='18sp', background_normal='',
                                background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)
        self.main_layout.add_widget(top_bar_layout)

        self.question_number_label = Label(text='Soru 1/10', font_size='24sp', color=(1, 1, 1, 1), size_hint_y=None,
                                           height=dp(50))
        self.main_layout.add_widget(self.question_number_label)

        self.color_image = Image(size_hint=(None, None), size=(dp(150), dp(150)), pos_hint={'center_x': 0.5})
        self.main_layout.add_widget(self.color_image)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.option_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),
                                               spacing=dp(10))
        self.option1_button = Button(text='Seçenek 1', font_size='20sp', background_normal='',
                                     background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with self.option1_button.canvas.before:
            self.option1_button.btn_color = Color(*self.option1_button.background_color)
            self.option1_button.btn_rect = RoundedRectangle(pos=self.option1_button.pos, size=self.option1_button.size,
                                                            radius=[dp(15)] * 4)
            self.option1_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option1_button.bind(on_press=lambda x: self.check_answer(self.option1_button.text))
        self.option_buttons_layout.add_widget(self.option1_button)

        self.option2_button = Button(text='Seçenek 2', font_size='20sp', background_normal='',
                                     background_color=(0.25, 0.45, 0.75, 1), color=(1, 1, 1, 1))
        with self.option2_button.canvas.before:
            self.option2_button.btn_color = Color(*self.option2_button.background_color)
            self.option2_button.btn_rect = RoundedRectangle(pos=self.option2_button.pos, size=self.option2_button.size,
                                                            radius=[dp(15)] * 4)
            self.option2_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option2_button.bind(on_press=lambda x: self.check_answer(self.option2_button.text))
        self.option_buttons_layout.add_widget(self.option2_button)
        self.main_layout.add_widget(self.option_buttons_layout)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.test_finish_button = Button(text='Testi Bitir', size_hint_y=None, height=dp(60), font_size='20sp',
                                         background_normal='', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        with self.test_finish_button.canvas.before:
            self.test_finish_button.btn_color = Color(*self.test_finish_button.background_color)
            self.test_finish_button.btn_rect = RoundedRectangle(pos=self.test_finish_button.pos,
                                                                size=self.test_finish_button.size, radius=[dp(15)] * 4)
            self.test_finish_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.test_finish_button.bind(on_press=self.finish_test)
        self.test_finish_button.disabled = True
        self.main_layout.add_widget(self.test_finish_button)

        self.main_layout.add_widget(BoxLayout())
        self.add_widget(self.main_layout)

        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.total_questions = 10
        self.selected_student = None
        self.test_started = False
        self.timer_event = None
        self.time_elapsed = 0
        self.test_questions_data = []

        self.loading_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.4),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5}, padding=dp(20), spacing=dp(10))
        self.loading_layout.add_widget(Label(text="Renk Soruları Yükleniyor...", font_size='20sp', color=(1, 1, 1, 1)))
        self.loading_progress = ProgressBar(max=100, value=0)
        self.loading_layout.add_widget(self.loading_progress)
        self.loading_popup = Popup(title='Yükleniyor', content=self.loading_layout, size_hint=(None, None),
                                   size=(dp(300), dp(200)), auto_dismiss=False)

    def start_test(self, student_name):
        # This method is almost identical to the base class, but calls a different question fetcher
        self.selected_student = student_name
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.time_elapsed = 0
        self.test_finish_button.disabled = True
        self.test_started = False
        self.test_questions_data = []
        self.loading_popup.open()
        threading.Thread(target=self._fetch_gemini_questions_thread).start()

    def _fetch_gemini_questions_thread(self):
        try:
            questions = self.fetch_gemini_questions()
            if questions:
                Clock.schedule_once(lambda dt: self._on_questions_loaded(questions), 0)
            else:
                Clock.schedule_once(
                    lambda dt: self._show_error_popup("Renk soruları yüklenemedi. Lütfen tekrar deneyin."), 0)
        except Exception as e:
            print(f"Renk sorusu yükleme hatası: {e}")
            Clock.schedule_once(lambda dt: self._show_error_popup(f"Bir hata oluştu: {e}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)

    def fetch_gemini_questions(self):
        prompt = """
        Bana 10 adet renk tanıma testi sorusu oluştur. Her soru için bir renk adı (Türkçe) ve iki seçenek (biri doğru cevap, diğeri yanlış bir renk adı) ver. JSON formatında yanıt ver. Renk adlarını Türkçe ve küçük harfle yaz.
         **ÖNEMLİ KISITLAMA:** Kullanacağın tüm renk adları (hem doğru cevap hem de seçeneklerdeki) SADECE aşağıdaki listeden olmalıdır: "kırmızı", "mavi", "yeşil", "sarı", "mor", "turuncu", "siyah", "beyaz", "pembe", "kahverengi", "gri". Bu listenin dışında hiçbir renk adı kullanma.

         Örnek:
        [
            {"color_name": "kırmızı", "correct_answer": "kırmızı", "options": ["kırmızı", "mavi"]},
            {"color_name": "yeşil", "correct_answer": "yeşil", "options": ["mor", "yeşil"]}
        ]
        Yanlış seçenekler her zaman farklı ve doğru cevaptan belirgin şekilde ayrı olsun. Sadece Türkçe renk adlarını kullan.
        """
        chatHistory = [{"role": "user", "parts": [{"text": prompt}]}]
        payload = {"contents": chatHistory, "generationConfig": {"responseMimeType": "application/json"}}
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        try:
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
            response.raise_for_status()
            result = response.json()
            json_string = result['candidates'][0]['content']['parts'][0]['text']
            questions = json.loads(json_string)
            return questions
        except Exception as e:
            print(f"API isteği hatası: {e}")
            return None

    def load_question(self):
        if self.current_question_index < len(self.test_questions_data):
            question_data = self.test_questions_data[self.current_question_index]
            self.question_number_label.text = f'Soru {self.current_question_index + 1}/{self.total_questions}'
            color_name = question_data["color_name"].lower()
            image_path = COLOR_IMAGE_MAP.get(color_name)
            if image_path and os.path.exists(image_path):
                self.color_image.source = image_path
            else:
                self.color_image.source = ''  # Fallback
                print(f"Uyarı: '{color_name}' için resim bulunamadı: {image_path}")

            options = question_data["options"]
            random.shuffle(options)
            self.option1_button.text = options[0]
            self.option2_button.text = options[1]
            self.enable_options()
        else:
            self.finish_test()

    # The rest of the methods are identical to BaseImageTestScreen, so we can just copy them
    _update_main_layout_bg = BaseImageTestScreen._update_main_layout_bg
    _on_questions_loaded = BaseImageTestScreen._on_questions_loaded
    _show_error_popup = BaseImageTestScreen._show_error_popup
    start_timer = BaseImageTestScreen.start_timer
    update_timer = BaseImageTestScreen.update_timer
    check_answer = BaseImageTestScreen.check_answer
    next_question = BaseImageTestScreen.next_question
    enable_options = BaseImageTestScreen.enable_options
    disable_options = BaseImageTestScreen.disable_options
    finish_test = BaseImageTestScreen.finish_test
    on_back_button_press = BaseImageTestScreen.on_back_button_press
    on_profile_button_press = BaseImageTestScreen.on_profile_button_press




class MathTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_konu = "Matematik Testi"
        self.background_color = (0.3, 0.7, 0.4, 1)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        top_bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=(0, dp(5), 0, dp(5)), spacing=dp(10))
        back_button = Button(text='<', size_hint_x=None, width=dp(50), font_size='24sp', background_normal='', background_color=(0.3, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)
        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))
        self.timer_label = Label(text="00:00", font_size='20sp', color=(1, 1, 1, 1), size_hint_x=None, width=dp(80))
        top_bar_layout.add_widget(self.timer_label)
        profile_button = Button(text='Profil', size_hint_x=None, width=dp(100), font_size='18sp', background_normal='', background_color=(0.3, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size, radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)
        self.main_layout.add_widget(top_bar_layout)

        self.question_number_label = Label(text='Soru 1/10', font_size='24sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(50))
        self.main_layout.add_widget(self.question_number_label)

        self.math_question_label = Label(text='Soru Yükleniyor...', font_size='32sp', color=(1, 1, 1, 1), size_hint_y=None, height=dp(100), halign='center')
        self.main_layout.add_widget(self.math_question_label)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.option_buttons_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140), spacing=dp(10))
        first_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        self.option1_button = Button(text='...', font_size='20sp', background_normal='', background_color=(0.3, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        with self.option1_button.canvas.before:
            self.option1_button.btn_color = Color(*self.option1_button.background_color)
            self.option1_button.btn_rect = RoundedRectangle(pos=self.option1_button.pos, size=self.option1_button.size, radius=[dp(15)] * 4)
            self.option1_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option1_button.bind(on_press=lambda x: self.check_answer(self.option1_button.text))
        first_row.add_widget(self.option1_button)

        self.option2_button = Button(text='...', font_size='20sp', background_normal='', background_color=(0.3, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        with self.option2_button.canvas.before:
            self.option2_button.btn_color = Color(*self.option2_button.background_color)
            self.option2_button.btn_rect = RoundedRectangle(pos=self.option2_button.pos, size=self.option2_button.size, radius=[dp(15)] * 4)
            self.option2_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.option2_button.bind(on_press=lambda x: self.check_answer(self.option2_button.text))
        first_row.add_widget(self.option2_button)
        self.option_buttons_layout.add_widget(first_row)
        self.main_layout.add_widget(self.option_buttons_layout)
        self.main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.test_finish_button = Button(text='Testi Bitir', size_hint_y=None, height=dp(60), font_size='20sp', background_normal='', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        with self.test_finish_button.canvas.before:
            self.test_finish_button.btn_color = Color(*self.test_finish_button.background_color)
            self.test_finish_button.btn_rect = RoundedRectangle(pos=self.test_finish_button.pos, size=self.test_finish_button.size, radius=[dp(15)] * 4)
            self.test_finish_button.bind(pos=update_button_canvas, size=update_button_canvas)
        self.test_finish_button.bind(on_press=self.finish_test)
        self.test_finish_button.disabled = True
        self.main_layout.add_widget(self.test_finish_button)

        self.main_layout.add_widget(BoxLayout())
        self.add_widget(self.main_layout)

        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.total_questions = 10
        self.selected_student = None
        self.test_started = False
        self.timer_event = None
        self.time_elapsed = 0
        self.test_questions_data = []

        self.loading_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5, 'center_y': 0.5}, padding=dp(20), spacing=dp(10))
        self.loading_layout.add_widget(Label(text="Matematik Soruları Yükleniyor...", font_size='20sp', color=(1, 1, 1, 1)))
        self.loading_progress = ProgressBar(max=100, value=0)
        self.loading_layout.add_widget(self.loading_progress)
        self.loading_popup = Popup(title='Yükleniyor', content=self.loading_layout, size_hint=(None, None), size=(dp(300), dp(200)), auto_dismiss=False)

    # --- DÜZELTME BURADA ---
    # MathTestScreen için doğru 'start_test' metodu tanımlandı.
    def start_test(self, student_name):
        self.selected_student = student_name
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.time_elapsed = 0
        self.test_finish_button.disabled = True
        self.test_started = False
        self.test_questions_data = []
        self.loading_popup.open()
        # API'den soru çekmek için doğru fonksiyon olan '_fetch_math_questions_thread' çağrılıyor.
        threading.Thread(target=self._fetch_math_questions_thread).start()


    def fetch_math_questions(self):
        prompt = """
        Bana 10 adet matematik sorusu oluştur. Sorular ilkokul seviyesinde olmalı ve toplama, çıkarma, çarpma ve bölme işlemlerini içermeli. Her soru için 2 seçenek ver. JSON formatında yanıt ver.
        Örnek:
        [
            {"question": "25 + 23 = ?", "correct_answer": "48", "options": ["48", "47"]},
            {"question": "12 - 4 = ?", "correct_answer": "8", "options": ["8", "9"]}
        ]
        - Toplama/çıkarma: 1-5000 arası sayılar.
        - Çarpma/bölme: 1-99 arası sayılar, sonuçlar tam sayı olmalı.
        - Her soruda 2 farklı seçenek olmalı ve doğru cevap seçenekler arasında bulunmalı.
        """
        chatHistory = [{"role": "user", "parts": [{"text": prompt}]}]
        payload = {
            "contents": chatHistory,
            "generationConfig": {
                "responseMimeType": "application/json",
                # responseSchema kısmını kaldırıyorum, çünkü bazı API'lar bu tür kısıtlamaları desteklemiyor veya hatalı yanıtlar üretebiliyor.
                # Daha esnek bir JSON yanıtı almak için bu kaldırıldı.
            }
        }
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

        try:
            # API isteği için zaman aşımı (timeout) eklenmesi, uygulamanın donmasını engeller.
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
            response.raise_for_status()  # HTTP hatalarını (4xx, 5xx) yakala
            result = response.json()

            # API'dan gelen yanıtın yapısını kontrol et.
            if 'candidates' in result and result['candidates'][0]['content']['parts'][0]['text']:
                json_string = result['candidates'][0]['content']['parts'][0]['text']

                # Bazen API'dan gelen JSON yanıtı, bir kod bloğu içinde olabiliyor. Bu durumda, JSON verisini temizle.
                if json_string.startswith("```json") and json_string.endswith("```"):
                    json_string = json_string[7:-3].strip()

                questions = json.loads(json_string)

                # Yanıtın bir liste olup olmadığını kontrol et
                if isinstance(questions, list) and all(isinstance(q, dict) for q in questions):
                    print("API'den matematik soruları başarıyla çekildi.")
                    return questions
                else:
                    print("API'den beklenen formatta (liste) yanıt alınamadı.")
                    return None
            else:
                print("API'den beklenen formatta yanıt alınamadı.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir ağ hatası oluştu: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"API yanıtı JSON olarak ayrıştırılamadı: {e}")
            return None
        except Exception as e:
            print(f"Genel bir hata oluştu: {e}")
            return None

    def _fetch_math_questions_thread(self):
        """Gemini API'den matematik sorularını senkron olarak çeken thread."""
        try:
            questions = self.fetch_math_questions()
            if questions:
                Clock.schedule_once(lambda dt: self._on_questions_loaded(questions), 0)
            else:
                Clock.schedule_once(lambda dt: self._show_error_popup("Matematik soruları yüklenemedi. API yanıtını kontrol edin."), 0)
        except Exception as e:
            print(f"Matematik soruları yükleme hatası: {e}")
            Clock.schedule_once(lambda dt: self._show_error_popup(f"Bir hata oluştu: {e}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)

    def load_question(self):
        if self.current_question_index < len(self.test_questions_data):
            question_data = self.test_questions_data[self.current_question_index]
            self.question_number_label.text = f'Soru {self.current_question_index + 1}/{self.total_questions}'
            self.math_question_label.text = question_data["question"]
            options = question_data.get("options", [])[:2]
            random.shuffle(options)
            if len(options) >= 2:
                self.option1_button.text = options[0]
                self.option2_button.text = options[1]
            self.enable_options()
        else:
            self.finish_test()

    _update_main_layout_bg = BaseImageTestScreen._update_main_layout_bg
    _on_questions_loaded = BaseImageTestScreen._on_questions_loaded
    _show_error_popup = BaseImageTestScreen._show_error_popup
    start_timer = BaseImageTestScreen.start_timer
    update_timer = BaseImageTestScreen.update_timer
    check_answer = BaseImageTestScreen.check_answer
    next_question = BaseImageTestScreen.next_question
    enable_options = BaseImageTestScreen.enable_options
    disable_options = BaseImageTestScreen.disable_options
    finish_test = BaseImageTestScreen.finish_test
    on_back_button_press = BaseImageTestScreen.on_back_button_press
    on_profile_button_press = BaseImageTestScreen.on_profile_button_press




# 6. Sayfa: ReportScreen (Rapor Sayfası) - Birleştirilmiş
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.background_color = (0.7, 0.6, 0.4, 1)

        with self.main_layout.canvas.before:
            self.main_layout.bg_color_instruction = Color(*self.background_color)
            self.main_layout.bg_rect_instruction = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            self.main_layout.bind(size=self._update_main_layout_bg, pos=self._update_main_layout_bg)

        top_bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50),
                                   padding=(0, dp(5), 0, dp(5)), spacing=dp(10))
        back_button = Button(text='<', size_hint_x=None, width=dp(50), font_size='24sp', background_normal='',
                             background_color=(0.96, 0.87, 0.70, 1), color=(0, 0, 0, 1))
        with back_button.canvas.before:
            back_button.btn_color = Color(*back_button.background_color)
            back_button.btn_rect = RoundedRectangle(pos=back_button.pos, size=back_button.size, radius=[dp(10)] * 4)
            back_button.bind(pos=update_button_canvas, size=update_button_canvas)
        back_button.bind(on_press=self.on_back_button_press)
        top_bar_layout.add_widget(back_button)
        top_bar_layout.add_widget(BoxLayout(size_hint_x=1))
        profile_button = Button(text='Profil', size_hint_x=None, width=dp(100), font_size='18sp', background_normal='',
                                background_color=(0.96, 0.87, 0.70, 1), color=(0, 0, 0, 1))
        with profile_button.canvas.before:
            profile_button.btn_color = Color(*profile_button.background_color)
            profile_button.btn_rect = RoundedRectangle(pos=profile_button.pos, size=profile_button.size,
                                                       radius=[dp(10)] * 4)
            profile_button.bind(pos=update_button_canvas, size=update_button_canvas)
        profile_button.bind(on_press=self.on_profile_button_press)
        top_bar_layout.add_widget(profile_button)
        self.main_layout.add_widget(top_bar_layout)

        self.report_title_label = Label(text='Rapor', font_size='26sp', color=(1, 1, 1, 1), size_hint_y=None,
                                        height=dp(50))
        self.main_layout.add_widget(self.report_title_label)

        self.report_scroll_view = ScrollView(size_hint_y=1)
        self.report_content_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(10))
        self.report_content_layout.bind(minimum_height=self.report_content_layout.setter('height'))
        with self.report_content_layout.canvas.before:
            self.report_bg_color = Color(1, 1, 1, 1)
            self.report_bg_rect = RoundedRectangle(pos=self.report_content_layout.pos,
                                                   size=self.report_content_layout.size, radius=[dp(15)] * 4)
            self.report_content_layout.bind(pos=self._update_report_layout_canvas,
                                            size=self._update_report_layout_canvas)
        self.report_text_content = Label(text="Rapor Yükleniyor...", color=(0, 0, 0, 1), font_size='18sp',
                                         size_hint_y=None, halign='left', valign='top', markup=True)
        self.report_text_content.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.report_content_layout.bind(width=self._on_content_layout_width_change)
        self.report_content_layout.add_widget(self.report_text_content)
        self.report_scroll_view.add_widget(self.report_content_layout)
        self.main_layout.add_widget(self.report_scroll_view)
        self.add_widget(self.main_layout)

    def _update_main_layout_bg(self, instance, value):
        instance.bg_rect_instruction.pos = instance.pos
        instance.bg_rect_instruction.size = instance.size
        instance.bg_color_instruction.rgba = self.background_color

    def _update_report_layout_canvas(self, instance, value):
        self.report_bg_rect.pos = instance.pos
        self.report_bg_rect.size = instance.size

    def on_back_button_press(self, instance):
        self.manager.current = 'test_selection_screen'

    def on_profile_button_press(self, instance):
        self.manager.current = 'user_profile_screen'

    def update_report(self, report_data):
        self.report_text_content.text = "Gemini Yorumu Oluşturuluyor..."
        threading.Thread(target=self._fetch_gemini_comment_thread, args=(report_data,)).start()

    def _fetch_gemini_comment_thread(self, report_data):
        prompts = {
            "Hayvan Tanıma Testi": "Bu hayvan tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, hayvanlar hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
            "Besin Tanıma Testi": "Bu besin tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, besinler hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
            "Nesne Tanıma Testi": "Bu nesne tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, nesneler hakkındaki genel bilgi düzeyini ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
            "Meyve Sebze Tanıma Testi": "Bu meyve-sebze tanıma testi sonuçlarına göre öğrencinin görsel algı, tanıma becerilerini, sağlıklı beslenme farkındalığını ve dikkat süresini değerlendirip, gelişim alanları için öneriler sun.",
            "Renk Tanıma Testi": "Bu renk tanıma testi sonuçlarına göre öğrencinin renkleri tanıma becerisini, görsel algısını ve dikkat süresini analiz et, gelişim alanlarını belirt ve önerilerde bulun.",
            "Matematik Testi": "Bu matematik testi sonuçlarına göre öğrencinin temel işlem becerilerini, problem çözme yeteneğini ve dikkat süresini analiz et, güçlü ve zayıf yönlerini belirt ve gelişim için önerilerde bulun."
        }

        base_prompt = f"""
        Aşağıdaki öğrenci test sonuçlarına göre detaylı bir rapor ve yorum oluştur:
        Öğrenci Adı: {report_data['ogrenci_adi']}
        Konu: {report_data['konu']}
        Toplam Soru: {report_data['toplam_soru']}
        Doğru Cevap: {report_data['dogru_cevap']}
        Yanlış Cevap: {report_data['yanlis_cevap']}
        Boş Cevap: {report_data['bos_cevap']}
        Başarı Yüzdesi: %{report_data['yuzde']}
        Test Süresi: {report_data['sure']} saniye

        Yorum İsteği: {prompts.get(report_data['konu'], "Lütfen öğrencinin performansını değerlendir.")}
        Motivasyonunu artıracak pozitif bir dil kullan.
        """

        try:
            chatHistory = [{"role": "user", "parts": [{"text": base_prompt}]}]
            payload = {"contents": chatHistory}
            apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
            response.raise_for_status()
            result = response.json()
            gemini_comment = result['candidates'][0]['content']['parts'][0]['text']
            Clock.schedule_once(lambda dt: self._update_report_ui(report_data, gemini_comment))
        except Exception as e:
            print(f"Gemini API hatası: {e}")
            Clock.schedule_once(
                lambda dt: self._update_report_ui(report_data, "Rapor yorumu alınırken bir hata oluştu."), 0)

    def _update_report_ui(self, report_data, gemini_comment):
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
        Clock.schedule_once(self._post_text_update_layout, 0.1)

    def _post_text_update_layout(self, dt):
        available_width = self.report_content_layout.width - (dp(15) * 2)
        self.report_text_content.text_size = (available_width if available_width > 0 else dp(1), None)
        self.report_text_content.texture_update()
        self.report_text_content.height = self.report_text_content.texture_size[1]

    def _on_content_layout_width_change(self, instance, width):
        available_width = width - (dp(15) * 2)
        self.report_text_content.text_size = (available_width if available_width > 0 else dp(1), None)


# Ana Uygulama Sınıfı
class MobilEgitimApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.selected_student = None
        self.sm.current_test_type = None

        # Tüm ekranları ScreenManager'a ekle
        self.sm.add_widget(LoginScreen(name='login_screen'))
        self.sm.add_widget(UserProfileScreen(name='user_profile_screen'))
        self.sm.add_widget(TestSelectionScreen(name='test_selection_screen'))
        self.sm.add_widget(StudentSelectionScreen(name='student_selection_screen'))
        self.sm.add_widget(AnimalTestScreen(name='animal_test_screen'))
        self.sm.add_widget(FoodTestScreen(name='food_test_screen'))
        self.sm.add_widget(ObjectTestScreen(name='object_test_screen'))
        self.sm.add_widget(FruitVegetableTestScreen(name='fruit_vegetable_test_screen'))
        self.sm.add_widget(ColorTestScreen(name='color_test_screen'))
        self.sm.add_widget(MathTestScreen(name='math_test_screen'))
        self.sm.add_widget(ReportScreen(name='report_screen'))

        return self.sm


if __name__ == '__main__':
    MobilEgitimApp().run()