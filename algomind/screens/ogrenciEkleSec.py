from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp  # MDApp'e erişim için import ettik.


# KV dosyasındaki StudentCard'ın Python tarafındaki tanımını yapıyoruz.
class StudentCard(BoxLayout):
    student_id = StringProperty('')
    student_name = StringProperty('')
    avatar_source = StringProperty('algomind/assets/profile.png')


# OgrenciYonetimEkrani artık MDScreen'den türemeli.
class OgrenciYonetimEkrani(Screen):
    # .kv dosyasındaki yeni id'lere karşılık gelen property'ler
    student_list_grid = ObjectProperty(None)
    ad_input = ObjectProperty(None)
    soyad_input = ObjectProperty(None)
    yas_input = ObjectProperty(None)
    hassasiyet_input = ObjectProperty(None)
    sevdigi_seyler_input = ObjectProperty(None)
    egitim_durumu_input = ObjectProperty(None)
    iletisim_duzeyi_input = ObjectProperty(None)
    all_students_data = ListProperty([])
    _data_loaded = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        if not self._data_loaded:
            self.load_initial_data()
            self._data_loaded = True

    def load_initial_data(self):
        self.all_students_data = [
            {'id': '0040 101', 'name': 'Yred Mağe', 'avatar': 'algomind/assets/profile.png'},
            {'id': '0040 224', 'name': 'Öpla Uim', 'avatar': 'algomind/assets/profile.png'},
            {'id': '0039 876', 'name': 'Ahmet Yılmaz', 'avatar': 'algomind/assets/profile.png'},
            {'id': '0041 345', 'name': 'Ayşe Kaya', 'avatar': 'algomind/assets/profile.png'},
            {'id': '0041 567', 'name': 'Zeynep Demir', 'avatar': 'algomind/assets/profile.png'},
            {'id': '0042 111', 'name': 'Mustafa Can', 'avatar': 'algomind/assets/profile.png'},
        ]
        self.populate_student_list(self.all_students_data)

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
        adi = self.ids.ad_input.text
        soyadi = self.ids.soyad_input.text
        yas = self.ids.yas_input.text
        hassasiyetler = self.ids.hassasiyet_input.text
        sevdigi_seyler = self.ids.sevdigi_seyler_input.text
        egitim_durumu = self.ids.egitim_durumu_input.text
        iletisim_duzeyi = self.ids.iletisim_duzeyi_input.text

        cinsiyet = "Belirtilmedi"
        if self.ids.cinsiyet_kadin.active:
            cinsiyet = "Kadın"
        elif self.ids.cinsiyet_erkek.active:
            cinsiyet = "Erkek"

        print("--- Yeni Öğrenci Eklendi ---")
        print(f"Adı: {adi}")
        print(f"Soyadı: {soyadi}")
        print(f"Yaş: {yas}")
        print(f"Cinsiyet: {cinsiyet}")
        print(f"Hassasiyetleri: {hassasiyetler}")
        print(f"Sevdiği Şeyler: {sevdigi_seyler}")
        print(f"Eğitim Durumu: {egitim_durumu}")
        print(f"İletişim Düzeyi: {iletisim_duzeyi}")

        self.ids.ad_input.text = ""
        self.ids.soyad_input.text = ""
        self.ids.yas_input.text = ""
        self.ids.hassasiyet_input.text = ""
        self.ids.sevdigi_seyler_input.text = ""
        self.ids.egitim_durumu_input.text = ""
        self.ids.iletisim_duzeyi_input.text = ""
        self.ids.cinsiyet_kadin.active = False
        self.ids.cinsiyet_erkek.active = False

        self.populate_student_list(self.all_students_data)
        self.ids.content_manager.current = 'secim_view'

    def go_to_test_secim(self):
        """Test seçimi ekranına geçiş yapar."""
        print("Test sayfasına geçiliyor...")
        # Ana ScreenManager'a erişerek ekran değiştiriyoruz.
        self.manager.current = 'test_secim'

    # Bu metot, menü butonuna basıldığında çağrılır.
    def toggle_navigation_drawer(self):
        """Navigation drawer'ı açıp kapatır."""
        app = MDApp.get_running_app()
        nav_drawer = app.root.ids.nav_drawer
        nav_drawer.set_state("open" if nav_drawer.state == "close" else "close")

    def search_students(self, search_text):
        search_text = search_text.lower()
        if not search_text:
            self.populate_student_list(self.all_students_data)
            return
        filtered_list = [
            student for student in self.all_students_data
            if search_text in student['name'].lower() or search_text in student['id']
        ]
        self.populate_student_list(filtered_list)

