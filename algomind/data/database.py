import requests
import os

API_BASE_URL = "http://35.202.188.175:8080"  # VM IP adresin
TOKEN_FILE = "auth_token.txt"

class AuthService:
    def do_signup(self, email, password, role, ad, soyad, username):
        try:
            # DÜZELTME: Sunucu 'ad' ve 'soyad' yerine 'first_name' ve 'last_name' bekliyor.
            payload = {
                "email": email,
                "password": password,
                "role": role,
                "username": username,
                "first_name": ad,
                "last_name": soyad
            }
            response = requests.post(
                f"{API_BASE_URL}/signup",
                json=payload  # Veri JSON formatında gönderiliyor
            )
            if response.status_code == 200:
                return True, "Signup successful"
            else:
                return False, response.json().get("detail", "Signup failed")
        except Exception as e:
            return False, str(e)

    def login(self, email, password):
        try:
            # DÜZELTME: Sunucu JSON veri bekliyor, bu yüzden 'json=' kullanıyoruz.
            # Sunucu e-posta alanı için 'username' anahtarını bekliyor.
            payload = {'username': email, 'password': password}
            response = requests.post(
                f"{API_BASE_URL}/login",
                json=payload
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                self._save_token(token)
                return True, "Login successful"
            else:
                try:
                    detail = response.json().get("detail", "Login failed")
                except requests.exceptions.JSONDecodeError:
                    detail = response.text
                return False, detail
        except Exception as e:
            return False, str(e)

    def _save_token(self, token):
        with open(TOKEN_FILE, "w") as f:
            f.write(token)

    def get_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                return f.read().strip()
        return None

    def get_user_role(self):
        token = self.get_token()
        if not token:
            return None
        try:
            response = requests.get(
                f"{API_BASE_URL}/user/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json().get("role")
            return None
        except Exception:
            return None

auth_service = AuthService()