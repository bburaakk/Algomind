# Düzeltme: psycopg2 yerine pg8000 kullanılıyor
import pg8000.dbapi as pg

# PostgreSQL bağlantı bilgileri
DB_HOST = "192.168.1.103"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Tarsua1+20+6"


def get_connection():
    """PostgreSQL veritabanı bağlantısını pg8000 ile döndürür."""
    try:
        conn = pg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None


def init_db_users():
    """Veritabanını başlatır ve kullanıcı tablosunu oluşturur."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # DÜZELTME: 'ad' ve 'soyad' sütunları eklendi.
            cur.execute(
                "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE, ad VARCHAR(50), soyad VARCHAR(50), email VARCHAR(100) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL, role VARCHAR(50) NOT NULL);")
            conn.commit()
            cur.close()
            conn.close()
            print("Veritabanı ve 'users' tablosu başarıyla başlatıldı.")
        except Exception as e:
            print(f"Tablo oluşturulurken hata oluştu: {e}")
            if conn:
                conn.close()
    else:
        print("Veritabanı başlatılamadı.")


def create_user(username, ad, soyad, email, password, role="ogretmen"):
    """Yeni bir kullanıcı oluşturur ve veritabanına kaydeder."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cur.fetchone():
                cur.close()
                conn.close()
                return False, "Bu kullanıcı adı veya e-posta zaten mevcut."

            # DÜZELTME: 'ad' ve 'soyad' bilgileri de INSERT sorgusuna eklendi.
            cur.execute(
                "INSERT INTO users (username, ad, soyad, email, password, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, ad, soyad, email, password, role)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True, "Kayıt başarılı."
        except Exception as e:
            if conn:
                conn.close()
            return False, f"Veritabanı hatası: {e}"
    else:
        return False, "Veritabanına bağlanılamadı."


def verify_user(username, password, role):
    """Kullanıcı adı, şifre ve rolü kontrol eder."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM users WHERE username = %s AND password = %s AND role = %s",
                (username, password, role)
            )
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user:
                return True
            else:
                return False
        except Exception as e:
            if conn:
                conn.close()
            print(f"Veritabanı doğrulama hatası: {e}")
            return False
    else:
        print("Veritabanına bağlanılamadı.")
        return False

