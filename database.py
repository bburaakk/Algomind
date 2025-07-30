# algomind/data/database.py

import requests
from kivy.app import App

API_URL = "???"  # GCloud'da değişecek

def verify_user(email, password):
    try:
        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            token = response.json().get("access_token")
            App.get_running_app().token = token
            App.get_running_app().logged_in_user = email
            return True
        else:
            return False
    except Exception as e:
        print("Hata:", e)
        return False

def create_user(email, password):
    try:
        response = requests.post(f"{API_URL}/signup", json={"email": email, "password": password})
        if response.status_code == 201:
            return True, "Kayıt başarılı"
        else:
            return False, response.json().get("detail", "Kayıt başarısız")
    except Exception as e:
        return False, str(e)
