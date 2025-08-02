# Ortak ekran erişim izinleri
COMMON_SCREENS = [
    'test_screen',
    'rapor_ekrani_screen',
    'profile_screen',
    'test_secim',
    'ogrenciEkleSec'
]

# Rol tabanlı ekran erişim izinleri
SCREEN_PERMISSIONS = {
    'ogretmen': COMMON_SCREENS,
    'veli': COMMON_SCREENS
}

def can_access_screen(user_role, screen_name):
    """
    Kullanıcının belirtilen ekrana erişip erişemeyeceğini kontrol eder.

    Args:
        user_role (str): Kullanıcının rolü (örn: 'ogretmen', 'veli').
        screen_name (str): Erişilmek istenen ekranın adı.

    Returns:
        bool: Kullanıcının ekrana erişim izni varsa True, yoksa False.
    """
    # Giriş ve kayıt ekranlarına her zaman izin ver
    if screen_name in ['login_screen', 'signup_screen']:
        return True

    if not user_role or user_role not in SCREEN_PERMISSIONS:
        return False

    return screen_name in SCREEN_PERMISSIONS[user_role]
