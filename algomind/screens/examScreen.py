from algomind.screens.baseScreen import BaseScreen
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, DictProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
import threading
import random
from algomind.helpers import generate_test_questions, show_popup
from algomind.data.test_data import ANIMAL_DATA, FOOD_DATA, OBJECT_DATA, MEYVE_SEBZE_DATA, COLOR_IMAGE_MAP


class TestScreen(BaseScreen):
    time_elapsed = NumericProperty(0)
    formatted_time = StringProperty("00:00")
    student_name = StringProperty('Öğrenci')
    question_text = StringProperty('Soru Yükleniyor...')
    question_counter_text = StringProperty('Soru 0/0')

    # Test durumu özellikleri
    test_questions = ListProperty([])
    current_question_index = NumericProperty(0)
    correct_answers = NumericProperty(0)
    incorrect_answers = NumericProperty(0)
    test_konu = StringProperty("")
    is_loading = ObjectProperty(False)

    def on_enter(self, *args):
        """Ekran görüntülendiğinde test ortamını hazırlar."""
        app = MDApp.get_running_app()
        self.student_name = getattr(app, 'selected_student_name', 'Bilinmiyor')
        self.test_type = app.current_test_type

        # Zamanlayıcıyı ve test durumunu sıfırla
        self.reset_test_state()
        Clock.schedule_interval(self.update_timer, 1)

        # Testi yükle
        self.setup_test()

    def on_leave(self, *args):
        """Ekrandan ayrılırken zamanlayıcıyı durdurur."""
        Clock.unschedule(self.update_timer)
        self.reset_test_state()

    def reset_test_state(self):
        """Testle ilgili tüm değişkenleri başlangıç durumuna getirir."""
        self.time_elapsed = 0
        self.formatted_time = "00:00"
        self.test_questions = []
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.is_loading = False
        if self.ids.test_content_area:
            self.ids.test_content_area.clear_widgets()

    def setup_test(self):
        """Seçilen test türüne göre soruları hazırlar."""
        self.ids.test_content_area.clear_widgets()
        spinner = MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)), pos_hint={'center_x': .5, 'center_y': .5})
        self.ids.test_content_area.add_widget(spinner)
        self.is_loading = True

        # Soruları arkaplanda yükle
        threading.Thread(target=self._load_questions_thread).start()

    def _load_questions_thread(self):
        """Soruları arkaplan thread'inde yükler ve ana thread'de UI'ı günceller."""
        test_map = {
            'animal': ("Hayvan Tanıma Testi", ANIMAL_DATA, "hayvanlar_images"),
            'food': ("Besin Tanıma Testi", FOOD_DATA, "food_images"),
            'object': ("Nesne Tanıma Testi", OBJECT_DATA, "objects_images"),
            'fruit_vegetable': ("Meyve Sebze Tanıma Testi", MEYVE_SEBZE_DATA, "meyve_sebze_images"),
            'color': ("Renk Tanıma Testi", None, None),
            'math': ("Matematik Testi", None, None)
        }

        if self.test_type not in test_map:
            Clock.schedule_once(lambda dt: show_popup("Hata", "Geçersiz test türü seçildi."))
            return

        self.test_konu, data_dict, image_folder = test_map[self.test_type]

        questions = []
        if self.test_type in ['math', 'color']:
            questions = generate_test_questions(self.test_type)
        else:
            # Resimli testler için yerel soru oluşturma
            items = list(data_dict.keys())
            random.shuffle(items)
            for i in range(min(10, len(items))):
                correct_item = items[i]
                # Resim yolu projenizin yapısına göre ayarlanmalı
                image_path = f"algomind/assets/{image_folder}/{random.choice(data_dict[correct_item])}"

                wrong_items = [item for item in items if item != correct_item]
                options = [correct_item, random.choice(wrong_items)]
                random.shuffle(options)
                questions.append({
                    "image_path": image_path,
                    "correct_answer": correct_item,
                    "options": options
                })

        if not questions:
            Clock.schedule_once(lambda dt: self._on_questions_loaded(None))
            return

        self.test_questions = questions
        Clock.schedule_once(lambda dt: self._on_questions_loaded(self.test_questions))

    def _on_questions_loaded(self, questions):
        """Sorular yüklendiğinde çağrılır ve ilk soruyu gösterir."""
        self.is_loading = False
        self.ids.test_content_area.clear_widgets()

        if not questions:
            show_popup("Hata", "Sorular yüklenirken bir hata oluştu.")
            # Hata durumunda seçim ekranına geri dönülebilir
            MDApp.get_running_app().switch_screen('test_secim')
            return

        self.display_question()

    def display_question(self):
        """Mevcut soruyu ekranda gösterir."""
        self.ids.test_content_area.clear_widgets()
        question_data = self.test_questions[self.current_question_index]
        self.question_counter_text = f"Soru {self.current_question_index + 1}/{len(self.test_questions)}"

        # Test türüne göre arayüzü oluştur
        if self.test_type in ['animal', 'food', 'object', 'fruit_vegetable']:
            self.question_text = "Resimdeki nedir?"
            image = Image(source=question_data['image_path'], size_hint_y=0.5, allow_stretch=True)
            self.ids.test_content_area.add_widget(image)
        elif self.test_type == 'color':
            self.question_text = "Bu hangi renktir?"
            color_name = question_data["question"].lower()
            image_path = f"algomind/assets/{COLOR_IMAGE_MAP.get(color_name)}"
            image = Image(source=image_path, size_hint_y=0.5, allow_stretch=True)
            self.ids.test_content_area.add_widget(image)
        elif self.test_type == 'math':
            self.question_text = 'Aşağıdaki işlemi çözünüz'
            question_label = MDLabel(
                text=question_data['question'],
                halign='center',
                theme_text_color='Primary',
                font_style='H5',
                size_hint_y=None,
                height=dp(50)
            )
            self.ids.test_content_area.add_widget(question_label)

        # Seçenek butonlarını oluştur
        options_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(10))
        for option in question_data['options']:
            btn = MDRaisedButton(
                text=str(option),
                size_hint_y=None,
                height=dp(50),
                on_release=lambda x, o=option: self.check_answer(o)
            )
            options_layout.add_widget(btn)

        self.ids.test_content_area.add_widget(options_layout)

    def check_answer(self, selected_option):
        """Kullanıcının cevabını kontrol eder."""
        question_data = self.test_questions[self.current_question_index]
        if str(selected_option) == str(question_data['correct_answer']):
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1

        # Butonları geçici olarak devre dışı bırak
        for widget in self.ids.test_content_area.children:
            if isinstance(widget, MDBoxLayout):
                for button in widget.children:
                    button.disabled = True

        # Bir sonraki soruya geç
        Clock.schedule_once(self.next_question, 1.0)

    def next_question(self, dt):
        """Bir sonraki soruya geçer veya testi bitirir."""
        self.current_question_index += 1
        if self.current_question_index < len(self.test_questions):
            self.display_question()
        else:
            self.finish_test()

    def finish_test(self):
        """Testi bitirir, sonuçları kaydeder ve rapor ekranına geçer."""
        app = MDApp.get_running_app()
        total_questions = len(self.test_questions)
        percentage = (self.correct_answers / total_questions) * 100 if total_questions > 0 else 0

        app.last_test_result = {
            "ogrenci_adi": self.student_name,
            "konu": self.test_konu,
            "dogru_cevap": self.correct_answers,
            "yanlis_cevap": self.incorrect_answers,
            "bos_cevap": total_questions - (self.correct_answers + self.incorrect_answers),
            "toplam_soru": total_questions,
            "yuzde": round(percentage, 2),
            "sure": self.time_elapsed
        }
        app.switch_screen('rapor_ekrani_screen')

    def update_timer(self, dt):
        """Zamanlayıcıyı günceller."""
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.formatted_time = f"{minutes:02d}:{seconds:02d}"
