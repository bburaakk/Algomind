import psycopg2

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Tarsua1+20+6"


def get_connection():
    """PostgreSQL veritabanı bağlantısını döndürür."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None


def init_db_users():
    """Veritabanını başlatır ve kullanıcı tablosunu oluşturur."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users
                        (
                            id
                            SERIAL
                            PRIMARY
                            KEY,
                            username
                            VARCHAR
                        (
                            50
                        ) NOT NULL UNIQUE,
                            password VARCHAR
                        (
                            255
                        ) NOT NULL,
                            role VARCHAR
                        (
                            50
                        ) NOT NULL
                            );
                        """)
            conn.commit()
        conn.close()
        print("Veritabanı ve 'users' tablosu başarıyla başlatıldı.")
    else:
        print("Veritabanı başlatılamadı.")


def create_user(username, password, role="ogretmen"):
    """Yeni bir kullanıcı oluşturur ve veritabanına kaydeder."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Kullanıcı adının zaten var olup olmadığını kontrol et
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    return False, "Bu kullanıcı adı zaten mevcut."

                # Yeni kullanıcıyı ekle
                cur.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role)
                )
                conn.commit()
            conn.close()
            return True, "Kayıt başarılı."
        except Exception as e:
            conn.close()
            return False, f"Veritabanı hatası: {e}"
    else:
        return False, "Veritabanına bağlanılamadı."


def verify_user(username, password, role):
    """Kullanıcı adı, şifre ve rolü kontrol eder."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE username = %s AND password = %s AND role = %s",
                    (username, password, role)
                )
                user = cur.fetchone()
            conn.close()
            if user:
                return True
            else:
                return False
        except Exception as e:
            conn.close()
            print(f"Veritabanı doğrulama hatası: {e}")
            return False
    else:
        print("Veritabanına bağlanılamadı.")
        return False


# Bu satırları sadece test amaçlı kullanın, ana uygulamanızda zaten çağrılıyor.
if __name__ == '__main__':
    init_db_users()
import psycopg2

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Tarsua1+20+6"


def get_connection():
    """PostgreSQL veritabanı bağlantısını döndürür."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None


def init_db_users():
    """Veritabanını başlatır ve kullanıcı tablosunu oluşturur."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users
                        (
                            id
                            SERIAL
                            PRIMARY
                            KEY,
                            username
                            VARCHAR
                        (
                            50
                        ) NOT NULL UNIQUE,
                            password VARCHAR
                        (
                            255
                        ) NOT NULL,
                            role VARCHAR
                        (
                            50
                        ) NOT NULL
                            );
                        """)
            conn.commit()
        conn.close()
        print("Veritabanı ve 'users' tablosu başarıyla başlatıldı.")
    else:
        print("Veritabanı başlatılamadı.")


def create_user(username, password, role="ogretmen"):
    """Yeni bir kullanıcı oluşturur ve veritabanına kaydeder."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Kullanıcı adının zaten var olup olmadığını kontrol et
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    return False, "Bu kullanıcı adı zaten mevcut."

                # Yeni kullanıcıyı ekle
                cur.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role)
                )
                conn.commit()
            conn.close()
            return True, "Kayıt başarılı."
        except Exception as e:
            conn.close()
            return False, f"Veritabanı hatası: {e}"
    else:
        return False, "Veritabanına bağlanılamadı."


def verify_user(username, password, role):
    """Kullanıcı adı, şifre ve rolü kontrol eder."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE username = %s AND password = %s AND role = %s",
                    (username, password, role)
                )
                user = cur.fetchone()
            conn.close()
            if user:
                return True
            else:
                return False
        except Exception as e:
            conn.close()
            print(f"Veritabanı doğrulama hatası: {e}")
            return False
    else:
        print("Veritabanına bağlanılamadı.")
        return False


