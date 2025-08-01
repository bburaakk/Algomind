from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

from algomind.data.database import auth_service

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        self.role_spinner = Spinner(
            text="Select Role",
            values=["teacher", "parent"],
            size_hint=(1, 0.3)
        )

        self.signup_button = Button(text="Signup", size_hint=(1, 0.3))
        self.signup_button.bind(on_press=self.signup_user)

        self.login_button = Button(text="Go to Login", size_hint=(1, 0.3))
        self.login_button.bind(on_press=self.go_to_login)

        self.layout.add_widget(self.email_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.role_spinner)
        self.layout.add_widget(self.signup_button)
        self.layout.add_widget(self.login_button)

        self.add_widget(self.layout)

    def signup_user(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        role = self.role_spinner.text.strip()

        if not email or not password or role == "Select Role":
            self.show_popup("Error", "Please fill in all fields.")
            return

        success, message = auth_service.signup(email, password, role)

        if success:
            self.show_popup("Success", "Signup successful! Please login.")
            self.manager.current = "login"
        else:
            self.show_popup("Signup Failed", message)

    def go_to_login(self, instance):
        self.manager.current = "login"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text="Close", size_hint=(1, 0.3))
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()
