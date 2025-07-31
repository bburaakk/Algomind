import requests

API_URL = "http://34.69.3.147:8080" # GCP'ye deploy edince IP ya da domain yazılacak

def create_user(email, password, role="teacher"):
    try:
        response = requests.post(f"{API_URL}/signup", json={
            "email": email,
            "password": password,
            "role": role
        })
        if response.status_code == 200:
            return True, "Kayıt başarılı"
        else:
            return False, response.json().get("detail", "Bilinmeyen hata")
    except Exception as e:
        return False, f"Sunucu hatası: {str(e)}"

def verify_user(email, password):
    try:
        response = requests.post(f"{API_URL}/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            # Token dönebilir, burada sadece doğrulama kontrolü yapıyoruz
            token = response.json().get("access_token")
            return True  # Giriş başarılı
        else:
            return False
    except Exception as e:
        print(f"Giriş hatası: {str(e)}")
        return False
