# /home/burak/Belgeler/PythonProjects/Algomind/ogrenciEkleSec.py

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock


# KV dosyasındaki StudentCard'ın Python tarafındaki tanımını yapıyoruz.
# Bu, karta dinamik olarak veri atamamızı çok kolaylaştırır.
class StudentCard(BoxLayout):
    student_id = StringProperty('')
    student_name = StringProperty('')
    avatar_source = StringProperty('algomind/assets/default_avatar.png')  # Varsayılan resim


class OgrenciYonetimEkrani(Screen):
    # .kv dosyasındaki yeni id'lere karşılık gelen property'ler
    student_list_grid = ObjectProperty(None)

    # Form alanları için property'ler
    ad_input = ObjectProperty(None)
    soyad_input = ObjectProperty(None)
    yas_input = ObjectProperty(None)
    hassasiyet_input = ObjectProperty(None)
    sevdigi_seyler_input = ObjectProperty(None)
    egitim_durumu_input = ObjectProperty(None)
    iletisim_duzeyi_input = ObjectProperty(None)

    # Tüm öğrencilerin tam listesini tutmak için bir property
    all_students_data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # on_enter'da sadece bir kez çalışmasını sağlamak için bir bayrak
        self._data_loaded = False
        # Clock.schedule_once(self.load_initial_data, 0.5)

    def on_enter(self, *args):
        """Bu ekran göründüğünde çalışan metod."""
        # Veriyi sadece ilk girişte yükle
        if not self._data_loaded:
            self.load_initial_data()
            self._data_loaded = True

    def load_initial_data(self):
        """
        Başlangıçta veritabanından veya bir API'den öğrenci verilerini çeker.
        Bu metot sadece bir kez çağrılmalıdır.
        """
        # --- ÖRNEK VERİ ---
        # Gerçek uygulamada bu veriler veritabanından gelecek.
        self.all_students_data = [
            {'id': '0040 101', 'name': 'Yred Mağe', 'avatar': 'algomind/assets/avatar1.png'},
            {'id': '0040 224', 'name': 'Öpla Uim', 'avatar': 'algomind/assets/avatar2.png'},
            {'id': '0039 876', 'name': 'Ahmet Yılmaz', 'avatar': 'algomind/assets/avatar3.png'},
            {'id': '0041 345', 'name': 'Ayşe Kaya', 'avatar': 'algomind/assets/avatar4.png'},
            {'id': '0041 567', 'name': 'Zeynep Demir', 'avatar': 'algomind/assets/avatar5.png'},
            {'id': '0042 111', 'name': 'Mustafa Can', 'avatar': 'algomind/assets/avatar6.png'},
        ]
        # Başlangıçta tüm öğrencileri göster
        self.populate_student_list(self.all_students_data)

    def populate_student_list(self, student_list):
        """
        Verilen öğrenci listesine göre arayüzdeki öğrenci kartlarını oluşturur.
        """
        grid = self.ids.student_list_grid
        grid.clear_widgets()  # Önceki kartları temizle

        for student_data in student_list:
            card = StudentCard(
                student_id=student_data.get('id', ''),
                student_name=student_data.get('name', ''),
                avatar_source=student_data.get('avatar', 'algomind/assets/default_avatar.png')
            )
            grid.add_widget(card)

    def add_student(self):
        """'Öğrenciyi Ekle' butonuna basıldığında çalışır."""
        # Yeni formdaki inputlardan verileri al
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



        # Formu temizle
        self.ids.ad_input.text = ""
        self.ids.soyad_input.text = ""
        self.ids.yas_input.text = ""
        self.ids.hassasiyet_input.text = ""
        self.ids.sevdigi_seyler_input.text = ""
        self.ids.egitim_durumu_input.text = ""
        self.ids.iletisim_duzeyi_input.text = ""
        self.ids.cinsiyet_kadin.active = False
        self.ids.cinsiyet_erkek.active = False


        # Öğrenci eklendikten sonra listeyi yenile ve seçim ekranına dön
        self.populate_student_list(self.all_students_data)
        self.ids.content_manager.current = 'secim_view'

    def go_to_test_secim(self):
        """Test seçimi ekranına geçiş yapar."""
        print("Test sayfasına geçiliyor...")
        self.manager.current = 'test_secim'

    # Arama ve filtreleme için taslak metotlar
    def search_students(self, search_text):
        """Arama metnine göre öğrencileri filtreler."""
        search_text = search_text.lower()
        if not search_text:
            self.populate_student_list(self.all_students_data)
            return

        filtered_list = [
            student for student in self.all_students_data
            if search_text in student['name'].lower() or search_text in student['id']
        ]
        self.populate_student_list(filtered_list)