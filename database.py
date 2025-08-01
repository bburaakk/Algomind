import requests

API_URL = "http://35.202.188.175:8080"  # FastAPI sunucun

class AuthService:
    def __init__(self):
        self.token = None
        self.user_role = None

    def signup(self, email, password, role):
        payload = {
            "email": email,
            "password": password,
            "role": role
        }
        try:
            response = requests.post(f"{API_URL}/signup", json=payload)
            if response.status_code == 200:
                return True, "Registration successful"
            else:
                return False, response.json().get("detail", "Signup failed")
        except Exception as e:
            return False, str(e)

    def login(self, email, password):
        payload = {
            "username": email,
            "password": password
        }
        try:
            response = requests.post(f"{API_URL}/login", data=payload)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.user_role = response.json().get("role")
                return True, "Login successful"
            else:
                return False, response.json().get("detail", "Login failed")
        except Exception as e:
            return False, str(e)

    def get_token(self):
        return self.token

    def get_user_role(self):
        return self.user_role

auth_service = AuthService()
