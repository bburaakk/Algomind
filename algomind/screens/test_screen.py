from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock


class TestScreen(Screen):
    time_elapsed = NumericProperty(0)
    formatted_time = StringProperty("00:00")
    student_name = StringProperty('Öğrenci')

    def on_enter(self, *args):
        Clock.schedule_interval(self.update_timer, 1)

    def on_leave(self, *args):
        Clock.unschedule(self.update_timer)
        self.time_elapsed = 0
        self.formatted_time = "00:00"

    def update_timer(self, dt):
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.formatted_time = f"{minutes:02d}:{seconds:02d}"