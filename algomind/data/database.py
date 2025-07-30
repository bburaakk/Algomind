import sqlite3
import bcrypt

# Veritabanı dosyasının adı. Bu dosya, uygulamanın çalıştığı dizinde oluşturulacak.
DB_NAME = "algomind.db"

def get_db_connection():
    """Veritabanına yeni bir bağlantı oluşturur ve döndürür."""
    try:
        # connect() metodu dosya yoksa otomatik olarak oluşturur.
        conn = sqlite3.connect(DB_NAME)
        # Sonuçlara sütun adıyla erişebilmek için row_factory ayarı
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def init_db_users():
    """
    Veritabanını ve 'users' tablosunu (eğer mevcut değilse) oluşturur.
    Bu fonksiyon uygulamanın başında bir kez çağrılmalıdır.
    """
    conn = get_db_connection()
    if not conn:
        print("Veritabanı başlatılamadı.")
        return

    try:
        # UNIQUE kısıtlaması, aynı kullanıcı adının tekrar eklenmesini engeller.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        print(f"Veritabanı '{DB_NAME}' başarıyla başlatıldı/kontrol edildi.")
    except sqlite3.Error as e:
        print(f"Tablo oluşturulurken hata oluştu: {e}")
    finally:
        if conn:
            conn.close()

def init_db_ogrenci_bilgileri():
    pass

def create_user(username, password):
    """Yeni bir kullanıcı oluşturur ve şifresini hash'leyerek kaydeder."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if not conn:
        return False, "Veritabanı bağlantısı kurulamadı."

    # PostgreSQL'deki '%s' yerine SQLite'ta placeholder olarak '?' kullanılır.
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"

    try:
        # 'with conn:' bloğu, işlem başarılı olursa otomatik commit,
        # hata olursa rollback yapar.
        with conn:
            conn.execute(sql, (username, hashed_password.decode('utf-8')))
        return True, "Kullanıcı başarıyla oluşturuldu."
    except sqlite3.IntegrityError:
        # Bu hata, 'username' UNIQUE kısıtlaması nedeniyle kullanıcı adı zaten mevcutsa oluşur.
        return False, "Bu kullanıcı adı zaten alınmış."
    except sqlite3.Error as e:
        return False, f"Bir hata oluştu: {e}"
    finally:
        if conn:
            conn.close()

def verify_user(username, password):
    """Kullanıcı adı ve şifreyi veritabanındaki hash ile karşılaştırarak doğrular."""
    conn = get_db_connection()
    if not conn:
        return False

    # PostgreSQL'deki '%s' yerine SQLite'ta placeholder olarak '?' kullanılır.
    sql = "SELECT password_hash FROM users WHERE username = ?"

    try:
        cur = conn.cursor()
        cur.execute(sql, (username,))
        result = cur.fetchone() # Tek bir sonuç satırı alır

        if result is None:
            # Kullanıcı bulunamadı
            return False

        # row_factory sayesinde sütun adıyla veriye erişiyoruz
        stored_hash = result['password_hash'].encode('utf-8')

        # Kullanıcının girdiği şifre ile veritabanındaki hash'i karşılaştır
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True # Şifre doğru
        else:
            return False # Şifre yanlış
    except sqlite3.Error as e:
        print(f"Kullanıcı doğrulanırken hata: {e}")
        return False
    finally:
        if conn:
            conn.close()