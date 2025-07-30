from kivy.uix.screenmanager import Screen

class TestSecimEkrani(Screen):
    def go_to_profile(self):
        self.manager.current = 'profile'

    def go_to_test_screen(self):
        self.manager.current = 'test_screen'