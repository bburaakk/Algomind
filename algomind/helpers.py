from kivy.uix.popup import Popup
from kivy.uix.label import Label

def show_popup(title, message):
    """Ekranda bilgilendirme penceresi gösterir."""
    popup = Popup(title=title,
                  content=Label(text=message, halign='center'),
                  size_hint=(0.8, 0.3),
                  title_align='center')
    popup.open()