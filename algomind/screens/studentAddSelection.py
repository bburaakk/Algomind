import json
from algomind.screens.baseScreen import BaseScreen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest


class StudentCard(BoxLayout):
    student_id = StringProperty('')
    student_name = StringProperty('')
    avatar_source = StringProperty('algomind/assets/profile.png')

class OgrenciYonetimEkrani(BaseScreen):
    student_list_grid = ObjectProperty(None)
    all_students_data = ListProperty([])
    _data_loaded = False
    req = None  # UrlRequest nesnesini tutmak için

    def on_enter(self, *args):
        if not self._data_loaded:
            self.load_initial_data()

    def load_initial_data(self):
        try:
            self.req = UrlRequest(
                "http://35.202.188.175:8080/students",
                on_success=self._on_load_success,
                on_failure=self._on_load_failure,
                on_error=self._on_load_error,
                verify=False
            )
        except Exception as e:
            print(f"❌ Öğrenci verileri yüklenirken hata oluştu: {e}")

    def _on_load_success(self, request, result):
        students = result
        self.all_students_data = [
            {
                'id': str(student['id']),
                'name': f"{student['first_name']} {student['last_name']}",
                'avatar': 'algomind/assets/profile.png'
            }
            for student in students
        ]
        self.populate_student_list(self.all_students_data)
        self._data_loaded = True

    def _on_load_failure(self, request, result):
        print(f"⚠️ Öğrenci verileri yüklenemedi (Failure): {request.resp_status} - {result}")

    def _on_load_error(self, request, error):
        print(f"❌ Ağ bağlantı hatası (Load): {error}")

    def populate_student_list(self, student_list):
        grid = self.ids.student_list_grid
        grid.clear_widgets()
        for student_data in student_list:
            card = StudentCard(
                student_id=student_data.get('id', ''),
                student_name=student_data.get('name', ''),
                avatar_source=student_data.get('avatar', 'algomind/assets/profile.png')
            )
            grid.add_widget(card)

    def add_student(self):
        print("Öğrenci ekleme işlemi başlatılıyor...")
        try:
            veri = {
                "first_name": self.ids.ad_input.text,
                "last_name": self.ids.soyad_input.text,
                "age": int(self.ids.yas_input.text) if self.ids.yas_input.text.isdigit() else 0,
                "sensitivities": self.ids.hassasiyet_input.text,
                "interests": self.ids.sevdigi_seyler_input.text,
                "education_status": self.ids.egitim_durumu_input.text,
                "communication_level": self.ids.iletisim_duzeyi_input.text,
                "user_id": 1
            }
            print(f"Gönderilecek veri: {veri}")
            self._perform_add_student(veri)
        except Exception as e:
            print(f"❌ add_student içinde hata: {e}")

    def _perform_add_student(self, data):
        try:
            req_body = json.dumps(data)
            self.req = UrlRequest(
                "http://35.202.188.175:8080/students",
                req_body=req_body,
                req_headers={'Content-Type': 'application/json'},
                on_success=self._add_student_success,
                on_failure=self._add_student_failure,
                on_error=self._add_student_error,
                verify=False
            )
        except Exception as e:
            print(f"❌ _perform_add_student içinde hata: {e}")

    def _add_student_success(self, request, result):
        Clock.schedule_once(lambda dt: self._update_ui_after_add(result))

    def _add_student_failure(self, request, result):
        print(f"❌ API Hatası (Ekleme - Failure): {request.resp_status} - {result}")

    def _add_student_error(self, request, error):
        print(f"❌ Ağ bağlantı hatası (Ekleme - Error): {error}")

    def _update_ui_after_add(self, yeni_ogrenci):
        print(f"✅ Öğrenci başarıyla eklendi: {yeni_ogrenci}")
        self.all_students_data.append({
            'id': str(yeni_ogrenci['id']),
            'name': f"{yeni_ogrenci['first_name']} {yeni_ogrenci['last_name']}",
            'avatar': 'algomind/assets/profile.png'
        })
        self.populate_student_list(self.all_students_data)
        self.ids.ad_input.text = ""
        self.ids.soyad_input.text = ""
        self.ids.yas_input.text = ""
        self.ids.hassasiyet_input.text = ""
        self.ids.sevdigi_seyler_input.text = ""
        self.ids.egitim_durumu_input.text = ""
        self.ids.iletisim_duzeyi_input.text = ""
        self.ids.content_manager.current = 'secim_view'

    def search_students(self, search_text):
        search_text = search_text.lower().strip()
        if not search_text:
            self.populate_student_list(self.all_students_data)
            return
        filtered_list = [
            student for student in self.all_students_data
            if search_text in student['name'].lower()
        ]
        self.populate_student_list(filtered_list)

    def go_to_test_secim(self):
        self.manager.current = 'test_secim'

    def toggle_navigation_drawer(self):
        app = MDApp.get_running_app()
        nav_drawer = app.root.ids.nav_drawer
        nav_drawer.set_state("open" if nav_drawer.state == "close" else "close")
