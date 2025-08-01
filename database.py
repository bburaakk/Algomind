import requests
import os

API_BASE_URL = "http://35.202.188.175:8080"  # VM IP adresin
TOKEN_FILE = "auth_token.txt"

class AuthService:
    def signup(self, email, password, role):
        try:
            response = requests.post(
                f"{API_BASE_URL}/signup",
                json={"email": email, "password": password, "role": role}
            )
            if response.status_code == 200:
                return True, "Signup successful"
            else:
                return False, response.json().get("detail", "Signup failed")
        except Exception as e:
            return False, str(e)

    def login(self, email, password):
        try:
            response = requests.post(
                f"{API_BASE_URL}/login",
                data={"username": email, "password": password}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                self._save_token(token)
                return True, "Login successful"
            else:
                return False, response.json().get("detail", "Login failed")
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
