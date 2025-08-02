from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


def show_popup(title, message):
    """
    Ekranda bir bilgilendirme penceresi (popup) gösterir.

    Args:
        title (str): Pencerenin başlığı.
        message (str): Pencerede gösterilecek mesaj.
    """
    popup = Popup(title=title,
                  content=Label(text=message, halign='center'),
                  size_hint=(0.8, 0.3),
                  title_align='center')
    popup.open()


def clear_text_inputs(screen, fields):
    """
    Belirtilen ekrandaki metin giriş alanlarını temizler.

    Args:
        screen: Alanların bulunduğu ekran nesnesi.
        fields (list): Temizlenecek alanların id'lerinin listesi.
    """
    for field_id in fields:
        if hasattr(screen.ids, field_id):
            widget = screen.ids[field_id]
            if isinstance(widget, TextInput):
                widget.text = ""
