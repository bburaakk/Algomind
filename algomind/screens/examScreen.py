from algomind.screens.baseScreen import BaseScreen
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock


class TestScreen(BaseScreen):
    """
    Testin gerçekleştirildiği ekran.

    Bu ekran, test sırasında geçen süreyi gösteren bir zamanlayıcı içerir.

    Attributes:
        time_elapsed (NumericProperty): Geçen toplam saniye.
        formatted_time (StringProperty): Ekranda gösterilecek formatlanmış zaman (DD:SS).
        student_name (StringProperty): Testi çözen öğrencinin adı.
    """
    time_elapsed = NumericProperty(0)
    formatted_time = StringProperty("00:00")
    student_name = StringProperty('Öğrenci')

    def on_enter(self, *args):
        """
        Ekran görüntülendiğinde çağrılır.

        Zamanlayıcıyı başlatan bir saat (clock) olayını zamanlar.
        """
        Clock.schedule_interval(self.update_timer, 1)

    def on_leave(self, *args):
        """
        Ekrandan ayrılırken çağrılır.

        Zamanlayıcıyı durdurur ve zamanlayıcı değişkenlerini sıfırlar.
        """
        Clock.unschedule(self.update_timer)
        self.time_elapsed = 0
        self.formatted_time = "00:00"

    def update_timer(self, dt):
        """
        Zamanlayıcıyı günceller.

        Her saniye çağrılır, geçen süreyi artırır ve formatlanmış zamanı günceller.

        Args:
            dt (float): Çağrılar arasındaki geçen süre.
        """
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.formatted_time = f"{minutes:02d}:{seconds:02d}"
