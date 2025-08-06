from kivymd.uix.dialog import MDDialog
from algomind.screens.baseScreen import BaseScreen
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
import threading
import random
import os
from algomind.helpers import show_popup, save_test_to_db
from algomind.data.test_data import ANIMAL_DATA, FOOD_DATA, OBJECT_DATA, COLOR_DATA
from typing import Optional, List, Dict, Any
from kivy.uix.modalview import ModalView
import requests
import json
from algomind.data.apiConfig import API_BASE_URL



def generate_test_questions(test_type: str) -> Optional[List[Dict[str, Any]]]:
    """
    FastAPI backend'den belirtilen türde test soruları alır.
    Args:
        test_type (str): 'math' veya 'synonymAntonym' gibi test türü.
    Returns:
        list: Soru ve cevapları içeren bir liste veya hata durumunda None.
    """
    try:
        # FastAPI'deki create_test endpoint'ini kullan
        payload = {"test_type": test_type}
        response = requests.post(
            f"{API_BASE_URL}/create_test",
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        questions = result.get("questions", [])

        if isinstance(questions, list) and all(isinstance(q, dict) for q in questions):
            print(f"Backend'den {test_type} soruları başarıyla çekildi.")
            return questions
        else:
            print(f"Backend'den beklenen formatta ({test_type}) yanıt alınamadı.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Backend isteği sırasında bir ağ hatası oluştu: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Backend yanıtı JSON olarak ayrıştırılamadı: {e}")
        return None
    except Exception as e:
        print(f"Genel bir hata oluştu: {e}")
        return None


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
    test_title = StringProperty("")
    is_loading = ObjectProperty(False)
    spinner_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spinner_view = ModalView(size_hint=(None, None), size=(dp(100), dp(100)),
                                      background_color=(0, 0, 0, 0),
                                      auto_dismiss=False)
        spinner = MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)),
                            pos_hint={'center_x': .5, 'center_y': .5})
        self.spinner_view.add_widget(spinner)

    def on_pre_enter(self, *args):
        """Ekran görüntülenmeden hemen önce test durumunu sıfırlar."""
        self.reset_test_state()

    def on_enter(self, *args):
        """Ekran görüntülendiğinde test ortamını hazırlar."""
        app = MDApp.get_running_app()
        self.student_name = getattr(app, 'selected_student_name', 'Bilinmiyor')
        self.student_id = getattr(app, 'selected_student_id', None)
        self.test_type = app.current_test_type

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
        self.question_text = ''
        self.question_counter_text = ''

        if self.ids.get('image_area'):
            self.ids.image_area.clear_widgets()
        if self.ids.get('options_area'):
            self.ids.options_area.clear_widgets()

    def setup_test(self):
        """Seçilen test türüne göre soruları hazırlar."""
        if self.ids.get('image_area'):
            self.ids.image_area.clear_widgets()
        if self.ids.get('options_area'):
            self.ids.options_area.clear_widgets()

        self.spinner_view.open()
        self.is_loading = True
        threading.Thread(target=self._load_questions_thread).start()

    def _load_questions_thread(self):
        """Soruları arkaplan thread'inde yükler ve ana thread'de UI'ı günceller."""
        test_map = {
            'animal': ("Hayvan Tanıma Testi", ANIMAL_DATA, "animal_images"),
            'synonymAntonym': ("Eş ve Zıt Anlamlılar Testi", None, None),
            'object': ("Nesne Tanıma Testi", OBJECT_DATA, "objects_images"),
            'food': ("Yiyecekler Tanıma Testi", FOOD_DATA, "foods_images"),
            'color': ("Renk Tanıma Testi", COLOR_DATA, "color_images"),
            'math': ("Matematik Testi", None, None)
        }

        if self.test_type not in test_map:
            Clock.schedule_once(lambda dt: show_popup("Hata", "Geçersiz test türü seçildi."))
            return

        self.test_title, data_dict, image_folder = test_map[self.test_type]

        questions = []
        if self.test_type in ['math', 'synonymAntonym']:
            questions = generate_test_questions(self.test_type)
            if questions:
                for question in questions:
                    random.shuffle(question['options'])
        else:
            items = list(data_dict.keys())
            random.shuffle(items)
            for i in range(min(10, len(items))):
                correct_item = items[i]
                base_path = os.path.dirname(os.path.abspath(__file__))
                algomind_folder_path = os.path.dirname(base_path)
                image_path = os.path.join(algomind_folder_path, "assets", image_folder,
                                          random.choice(data_dict[correct_item]))
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
        self.spinner_view.dismiss()

        if not questions:
            show_popup("Hata", "Sorular yüklenirken bir hata oluştu.")
            MDApp.get_running_app().switch_screen('test_secim')
            return

        self.display_question()

        # Sorular yüklendiğinde ve ilk soru ekrana gelmeye hazır olduğunda zamanlayıcıyı başlat
        Clock.schedule_interval(self.update_timer, 1)

    def display_question(self):
        """Mevcut soruyu ekranda gösterir."""
        if self.ids.get('image_area'):
            self.ids.image_area.clear_widgets()
        if self.ids.get('options_area'):
            self.ids.options_area.clear_widgets()

        question_data = self.test_questions[self.current_question_index]
        self.question_counter_text = f"Soru {self.current_question_index + 1}/{len(self.test_questions)}"

        if self.test_type in ['animal', 'food', 'object', 'color']:
            if self.test_type == 'color':
                self.question_text = "Bu hangi renktir?"
            else:
                self.question_text = "Resimdeki nedir?"
            image_path_from_question = question_data['image_path']
            if os.path.exists(image_path_from_question):
                image = Image(source=image_path_from_question, allow_stretch=True, keep_ratio=True)
                self.ids.image_area.add_widget(image)
            else:
                placeholder = MDLabel(text="Görsel bulunamadı.", halign='center')
                self.ids.image_area.add_widget(placeholder)

        elif self.test_type == 'math':
            self.question_text = 'Aşağıdaki işlemi çözünüz'
            question_label = MDLabel(text=question_data['question'], halign='center', theme_text_color='Primary',
                                     font_style='H5', size_hint_y=None, height=dp(300))
            if self.ids.get('image_area'):
                self.ids.image_area.add_widget(question_label)

        elif self.test_type == 'synonymAntonym':
            self.question_text = 'Aşağıdaki kelimenin eş veya zıt anlamlısını seçiniz'
            question_label = MDLabel(text=question_data['question'], halign='center', theme_text_color='Primary',
                                     font_style='H5', size_hint_y=None, height=dp(50))
            if self.ids.get('image_area'):
                self.ids.image_area.add_widget(question_label)

        if self.ids.get('options_area'):
            for option in question_data['options']:
                btn = MDRaisedButton(
                    text=str(option),
                    size_hint_y=None,
                    height=dp(300),
                    size_hint_x=None,
                    width=dp(500),
                    font_size="28sp",
                    on_release=lambda x, o=option: self.check_answer(o)
                )
                self.ids.options_area.add_widget(btn)

    def check_answer(self, selected_option):
        """Kullanıcının cevabını kontrol eder ve bir sonraki soruya geçişi hazırlar."""
        question_data = self.test_questions[self.current_question_index]
        if str(selected_option) == str(question_data['correct_answer']):
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1

        if self.ids.get('image_area'):
            self.ids.image_area.clear_widgets()
        if self.ids.get('options_area'):
            self.ids.options_area.clear_widgets()

        self.spinner_view.open()
        Clock.schedule_once(self.next_question, 1.0)

    def next_question(self, dt):
        """Bir sonraki soruya geçer veya testi bitirir."""
        self.current_question_index += 1
        if self.current_question_index < len(self.test_questions):
            self.display_question()
        else:
            self.finish_test()
        self.spinner_view.dismiss()

    def finish_test(self):
        """Testi bitirir, sonuçları kaydeder ve rapor ekranına geçer."""
        app = MDApp.get_running_app()
        total_questions = len(self.test_questions)
        percentage = (self.correct_answers / total_questions) * 100 if total_questions > 0 else 0

        print(f"DEBUG: finish_test çağrıldı. Öğrenci ID: {self.student_id}, test_title: {self.test_title}")
        if self.student_id:
            print("DEBUG: save_test_to_db fonksiyonu çağrılıyor.")
            save_test_to_db(self.student_id, self.test_title)
            print("DEBUG: save_test_to_db fonksiyonu çağrıldı.")

        app.last_test_result = {
            "student_id": self.student_id,
            "ogrenci_adi": self.student_name,
            "konu": self.test_title,
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

    def finish_test_early(self):
        """
        Kullanıcı testi manuel olarak bitirmek istediğinde çağrılır.
        Bir onay penceresi gösterir.
        """
        Clock.unschedule(self.update_timer)  # Zamanlayıcıyı durdur

        # Onay penceresi oluştur
        dialog = MDDialog(
            title="Testi Bitir",
            text="Emin misiniz? Testi bitirdikten sonra sonuçlarınızı göreceksiniz.",
            buttons=[
                MDFlatButton(
                    text="İptal",
                    theme_text_color="Primary",
                    on_release=lambda x: self._dismiss_dialog_and_restart_timer(dialog)
                ),
                MDRaisedButton(
                    text="Evet, Bitir",
                    md_bg_color=MDApp.get_running_app().theme_cls.error_color,
                    on_release=lambda x: self._confirm_finish_test(dialog)
                ),
            ],
        )
        dialog.open()

    def _dismiss_dialog_and_restart_timer(self, dialog):
        """
        Onay penceresini kapatır ve zamanlayıcıyı yeniden başlatır.
        """
        dialog.dismiss()
        Clock.schedule_interval(self.update_timer, 1)  # Zamanlayıcıyı tekrar başlat

    def _confirm_finish_test(self, dialog):
        """
        Kullanıcı onayladıktan sonra testi bitirme işlemini başlatır.
        """
        dialog.dismiss()
        self.finish_test()