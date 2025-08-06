from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import requests


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


def save_test_to_db(student_id, test_title):
    api_url = 'http://35.202.188.175:8080/tests'
    data = {'student_id': student_id, 'test_title': test_title}
    print(f"DEBUG: Veritabanına test kaydediliyor. Veri: {data}")
    try:
        response = requests.post(api_url, json=data)
        print(f"DEBUG: API yanıtı alındı. Status Code: {response.status_code}, Response: {response.text}")
        if response.status_code == 200:
            print("Test başarıyla kaydedildi.")
        else:
            print(f"Test kaydedilemedi. Hata: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında bir hata oluştu: {e}")
