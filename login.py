from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from algomind.data.database import auth_service

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)

        self.login_button = Button(text="Login", size_hint=(1, 0.3))
        self.login_button.bind(on_press=self.login_user)

        self.signup_button = Button(text="Go to Signup", size_hint=(1, 0.3))
        self.signup_button.bind(on_press=self.go_to_signup)

        self.layout.add_widget(self.email_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.signup_button)

        self.add_widget(self.layout)

    def login_user(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.show_popup("Error", "Please fill in both fields.")
            return

        success, message = auth_service.login(email, password)

        if success:
            self.show_popup("Success", "Login successful!")
            role = auth_service.get_user_role()
            if role == "teacher":
                self.manager.current = "teacher_home"
            elif role == "parent":
                self.manager.current = "parent_home"
            else:
                self.show_popup("Error", "Unknown user role.")
        else:
            self.show_popup("Login Failed", message)

    def go_to_signup(self, instance):
        self.manager.current = "signup"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text="Close", size_hint=(1, 0.3))
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()
