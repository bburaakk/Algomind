from algomind.screens.baseScreen import BaseScreen
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
import threading
import random
import os
import requests
from algomind.helpers import generate_test_questions, show_popup
from algomind.data.test_data import ANIMAL_DATA, FOOD_DATA, OBJECT_DATA, COLOR_DATA
from kivy.lang import Builder
from kivy.uix.modalview import ModalView

Builder.load_file('algomind/UI/screens/examScreen.kv')


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

        # Zamanlayıcıyı başlat
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
            'animal': ("Hayvan Tanıma Testi", ANIMAL_DATA, "hayvanlar_images"),
            'synonymAntonym': ("Eş ve Zıt Anlamlı Kelimeler Testi", None, None),
            'object': ("Nesne Tanıma Testi", OBJECT_DATA, "objects_images"),
            'food': ("Yiyecekler Testi", FOOD_DATA, "foods_images"),
            'color': ("Renk Tanıma Testi", COLOR_DATA, "color_images"),
            'math': ("Matematik Testi", None, None)
        }

        if self.test_type not in test_map:
            Clock.schedule_once(lambda dt: show_popup("Hata", "Geçersiz test türü seçildi."))
            return

        self.test_title, data_dict, image_folder = test_map[self.test_type]

        questions = []
        if self.test_type in ['math', 'synonymAntonym']:
            questions = self._get_api_questions()
        else:
            questions = self._get_image_questions(data_dict, image_folder)

        if not questions:
            Clock.schedule_once(lambda dt: self._on_questions_loaded(None))
            return

        self.test_questions = questions
        Clock.schedule_once(lambda dt: self._on_questions_loaded(self.test_questions))

    def _get_api_questions(self):
        """API'den matematik ve eş/zıt anlamlı sorularını alır. Offline modda yerel sorular kullanır."""
        try:
            # Endpoint'teki test_type mapping'e göre
            api_test_type = 'synonymAntonym' if self.test_type == 'synonymAntonym' else 'math'
            
            payload = {"test_type": api_test_type}
            response = requests.post("http://35.202.188.175:8080/create_test", json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', [])
                # Seçenekleri karıştır
                for question in questions:
                    if 'options' in question:
                        random.shuffle(question['options'])
                return questions
            else:
                print(f"API hatası: {response.status_code} - {response.text}")
                return self._get_offline_questions()
        except requests.exceptions.RequestException as e:
            print(f"API bağlantı hatası: {e} - Offline moda geçiliyor")
            return self._get_offline_questions()
        except Exception as e:
            print(f"Genel hata: {e} - Offline moda geçiliyor")
            return self._get_offline_questions()

    def _get_image_questions(self, data_dict, image_folder):
        """Görsel tabanlı testler için soruları hazırlar."""
        questions = []
        items = list(data_dict.keys())
        random.shuffle(items)
        
        for i in range(min(10, len(items))):
            correct_item = items[i]
            base_path = os.path.dirname(os.path.abspath(__file__))
            algomind_folder_path = os.path.dirname(base_path)
            image_path = os.path.join(algomind_folder_path, "assets", image_folder, random.choice(data_dict[correct_item]))
            wrong_items = [item for item in items if item != correct_item]
            options = [correct_item, random.choice(wrong_items)]
            random.shuffle(options)
            questions.append({
                "image_path": image_path,
                "correct_answer": correct_item,
                "options": options
            })
        return questions

    def _on_questions_loaded(self, questions):
        """Sorular yüklendiğinde çağrılır ve ilk soruyu gösterir."""
        self.is_loading = False
        self.spinner_view.dismiss()

        if not questions:
            show_popup("Hata", "Sorular yüklenirken bir hata oluştu.")
            MDApp.get_running_app().switch_screen('test_secim')
            return

        self.display_question()

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
            question_label = MDLabel(text=question_data['question'], halign='center', theme_text_color='Primary', font_style='H5', size_hint_y=None, height=dp(300))
            if self.ids.get('image_area'):
                self.ids.image_area.add_widget(question_label)

        elif self.test_type == 'synonymAntonym':
            self.question_text = 'Aşağıdaki kelimenin eş veya zıt anlamlısını seçiniz'
            question_label = MDLabel(text=question_data['question'], halign='center', theme_text_color='Primary', font_style='H5', size_hint_y=None, height=dp(50))
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
        
        # Boş cevap sayısını hesapla
        bos_cevap = total_questions - (self.correct_answers + self.incorrect_answers)

        # Test sonucunu API'ye kaydet - test_id'yi kaldır
        test_result_data = {
            "student_id": self.student_id,
            "test_title": self.test_title,
            "ogrenci_adi": self.student_name,
            "konu": self.test_title,
            "dogru_cevap": self.correct_answers,
            "yanlis_cevap": self.incorrect_answers,
            "bos_cevap": bos_cevap,
            "toplam_soru": total_questions,
            "yuzde": round(percentage, 2),
            "sure": self.time_elapsed
        }

        print(f"DEBUG: finish_test çağrıldı. Öğrenci ID: {self.student_id}, test_title: {self.test_title}")
        
        # API'ye test sonucunu kaydet ve rapor oluştur
        if self.student_id:
            self._save_test_result_to_api(test_result_data)
        
        # App'e son test sonucunu kaydet (rapor ekranı için)
        app.last_test_result = test_result_data
        app.switch_screen('rapor_ekrani_screen')

    def _get_offline_questions(self):
        """API kullanılamadığında yerel sorular oluşturur."""
        questions = []
        
        if self.test_type == 'math':
            # Basit matematik soruları
            operations = ['+', '-', '*', '/']
            for i in range(10):
                if i < 4:  # Toplama
                    a, b = random.randint(1, 50), random.randint(1, 50)
                    correct = a + b
                    question_text = f"{a} + {b} = ?"
                elif i < 7:  # Çıkarma
                    a, b = random.randint(20, 50), random.randint(1, 19)
                    correct = a - b
                    question_text = f"{a} - {b} = ?"
                elif i < 9:  # Çarpma
                    a, b = random.randint(1, 10), random.randint(1, 10)
                    correct = a * b
                    question_text = f"{a} × {b} = ?"
                else:  # Bölme
                    b = random.randint(2, 10)
                    correct = random.randint(2, 10)
                    a = correct * b
                    question_text = f"{a} ÷ {b} = ?"
                
                wrong = correct + random.choice([-2, -1, 1, 2, 3])
                if wrong == correct:
                    wrong = correct + 5
                
                options = [str(correct), str(wrong)]
                random.shuffle(options)
                
                questions.append({
                    "question": question_text,
                    "correct_answer": str(correct),
                    "options": options
                })
        
        elif self.test_type == 'synonymAntonym':
            # Basit eş ve zıt anlamlı kelimeler
            word_pairs = [
                ("Büyük", "Küçük", "zıt", ["Küçük", "Dev"]),
                ("Hızlı", "Yavaş", "zıt", ["Yavaş", "Süratli"]),
                ("Mutlu", "Neşeli", "eş", ["Üzgün", "Neşeli"]),
                ("Soğuk", "Sıcak", "zıt", ["Sıcak", "Buzlu"]),
                ("Güzel", "Çirkin", "zıt", ["Çirkin", "Hoş"]),
                ("Akıllı", "Zeki", "eş", ["Aptal", "Zeki"]),
                ("Karanlık", "Aydınlık", "zıt", ["Aydınlık", "Gece"]),
                ("Yüksek", "Alçak", "zıt", ["Alçak", "Uzun"]),
                ("Temiz", "Kirli", "zıt", ["Kirli", "Pak"]),
                ("Sessiz", "Gürültülü", "zıt", ["Gürültülü", "Sakin"])
            ]
            
            random.shuffle(word_pairs)
            for word, pair_word, relation, options in word_pairs[:10]:
                if relation == "eş":
                    question_text = f"'{word}' kelimesinin eş anlamlısı nedir?"
                else:
                    question_text = f"'{word}' kelimesinin zıt anlamlısı nedir?"
                
                random.shuffle(options)
                questions.append({
                    "question": question_text,
                    "correct_answer": pair_word,
                    "options": options
                })
        
        return questions

    def _save_test_result_to_api(self, test_data):
        """Test sonucunu API'ye kaydeder ve rapor oluşturur. Offline modda basit rapor oluşturur."""
        try:
            # Önce test kaydını oluştur (eğer gerekiyorsa)
            test_id = self._create_test_record_if_needed()
            if test_id:
                test_data['test_id'] = test_id
            
            response = requests.post(
                "http://35.202.188.175:8080/create_test_result_and_report",
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"DEBUG: Test sonucu başarıyla kaydedildi. Result ID: {result.get('result_id')}, Report ID: {result.get('report_id')}")
                # Rapor metnini app'e kaydet
                app = MDApp.get_running_app()
                app.last_report_text = result.get('rapor_metni', 'Rapor oluşturulamadı.')
            else:
                print(f"API hatası: {response.status_code} - {response.text}")
                self._create_offline_report(test_data)
                
        except requests.exceptions.RequestException as e:
            print(f"API bağlantı hatası: {e} - Offline rapor oluşturuluyor")
            self._create_offline_report(test_data)
        except Exception as e:
            print(f"Genel hata: {e} - Offline rapor oluşturuluyor")
            self._create_offline_report(test_data)

    def _create_test_record_if_needed(self):
        """Tests tablosunda kayıt yoksa oluşturur, varsa ID'sini döner."""
        try:
            # Önce mevcut test kaydını kontrol et
            response = requests.get(f"http://35.202.188.175:8080/tests/{self.test_title}", timeout=5)
            
            if response.status_code == 200:
                test_data = response.json()
                return test_data.get('id')
            
            # Test kaydı yoksa oluştur  
            test_record = {
                "title": self.test_title,
                "description": f"{self.test_title} - Otomatik oluşturuldu",
                "question_count": len(self.test_questions),
                "test_type": self.test_type
            }
            
            response = requests.post("http://35.202.188.175:8080/tests/", json=test_record, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('id')
            else:
                print(f"Test kaydı oluşturulamadı: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Test kaydı kontrol/oluşturma hatası: {e}")
            return None

    def _create_offline_report(self, test_data):
        """API kullanılamadığında basit rapor oluşturur."""
        app = MDApp.get_running_app()
        
        success_rate = test_data['yuzde']
        total_questions = test_data['toplam_soru']
        correct_answers = test_data['dogru_cevap']
        test_time = test_data['sure']
        
        # Performans değerlendirmesi
        if success_rate >= 80:
            performance = "mükemmel"
            encouragement = "Tebrikler! Çok başarılısın."
        elif success_rate >= 60:
            performance = "iyi"
            encouragement = "Güzel bir performans sergiledi."
        elif success_rate >= 40:
            performance = "orta"
            encouragement = "Daha fazla çalışarak gelişebilirsin."
        else:
            performance = "geliştirilmeli"
            encouragement = "Endişelenme, pratik yaparak daha da iyileşeceksin."
        
        # Test süresine göre yorum
        if test_time < 120:  # 2 dakika
            time_comment = "Soruları çok hızlı çözdün."
        elif test_time < 300:  # 5 dakika
            time_comment = "Sorular için uygun süre harcadın."
        else:
            time_comment = "Sorular üzerinde dikkatlice düşündün."
        
        report_text = f"""
📊 {test_data['konu']} Raporu

Sevgili {test_data['ogrenci_adi']},

Bu testte {performance} bir performans gösterdin. {encouragement}

📈 Test Sonuçların:
• Toplam Soru: {total_questions}
• Doğru Cevap: {correct_answers}
• Başarı Oranı: %{success_rate}
• Test Süresi: {test_time // 60} dakika {test_time % 60} saniye

⏱️ {time_comment}

💡 Öneriler:
• Günlük pratik yapmaya devam et
• Yanlış yaptığın konuları tekrar et
• Sabırlı ol ve kendine güven

Başarılarının devamını diliyorum! 🌟
        """
        
        app.last_report_text = report_text.strip()

    def update_timer(self, dt):
        """Zamanlayıcıyı günceller."""
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.formatted_time = f"{minutes:02d}:{seconds:02d}"
