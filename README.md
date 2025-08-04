
# 🌈 Otizmli Çocuklar İçin Mobil Eğitim Uygulaması

Bu proje, otizmli çocuklara özel olarak tasarlanmış etkileşimli bir eğitim uygulamasıdır. Kivy tabanlı mobil uygulama; yapay zekâ destekli testler, kişiselleştirilmiş raporlar ve hikaye dinleme özellikleri sunar. FastAPI ile geliştirilen backend, Google Cloud altyapısında barındırılır ve Gemini API ile entegredir.

---

## 🚀 Özellikler

### 👨‍🏫 Kullanıcı Rolleri
- **Öğretmen**: Öğrenci ekleyebilir, test çözebilir, raporları görüntüleyebilir.
- **Veli**: Test çözebilir ancak öğrenci ekleyemez, rapor görüntüleyemez.

### 🧠 Yapay Zeka Destekli Testler
- Gemini API kullanılarak öğrenci profilinden yola çıkarak testler otomatik oluşturulur.

### 📊 Kişiselleştirilmiş Raporlar
- Test sonuçlarına göre AI tarafından açıklamalı ve görselleştirilmiş raporlar üretilir.

### 📚 Masal Dinleme Özelliği
- Kullanıcı seçimine göre Gemini API tarafından hikayeler oluşturulur, anında değiştirme ve tekrar dinleme özelliği bulunur.
- SSML formatında Google Cloud TTS ile seslendirilir.
- Mobil uygulamada sesli olarak dinletilir.

---

## 🧩 Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Frontend** | Python, [Kivy](https://kivy.org/), KivyMD |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy, JWT |
| **Veritabanı** | PostgreSQL (Google Cloud SQL) |
| **Yapay Zeka** | [Gemini API](https://deepmind.google/technologies/gemini) |
| **Metin Seslendirme** | Google Cloud Text-to-Speech (SSML) |
| **Bulut** | Google Cloud VM (Compute Engine), VPC, Firewall |

---

## 🗂️ Proje Mimarisi

```

📱 Kivy Mobile App
│
├── Login/Signup (JWT)
├── Test Çözme
├── Masal Dinleme
├── Öğrenci Görüntüleme/Ekleme (öğretmen)
│
▼
🌐 FastAPI Backend (Google Cloud VM)
├── /login, /signup, /students, /tests, /reports
├── Gemini API'ye test/rapor/masal talepleri
├── Google TTS ile SSML ses dönüşümü
├── PostgreSQL veritabanı işlemleri
│
▼
🧠 Gemini API (AI)
├── Test üretimi
├── Masal yazımı
├── Rapor oluşturma
│
▼
🔈 Google Cloud TTS
└── Hikaye seslendirme (SSML)

🛢️ PostgreSQL (Cloud SQL)
├── users
├── students
├── tests
└── reports

````

---

## 📑 API Endpointleri

### ✅ Authentication
- `POST /signup` – Kullanıcı kaydı
- `POST /login` – JWT token ile giriş

### 👨‍🎓 Öğrenci
- `GET /students` – Öğrencileri listele (öğretmene özel)
- `POST /students` – Yeni öğrenci ekle
- `GET /students/{id}` – Öğrenci detayları
- `GET /students/{id}/reports-summary` – Rapor özeti
- `GET /students/{id}/reports-detailed` – Detaylı rapor

### 🧪 Test
- `GET /tests/` – Tüm testleri getir
- `POST /tests/` – Yeni test oluştur (AI ile)

### 📈 Rapor
- `POST /reports/` – Rapor oluştur
- `GET /reports/` – Tüm raporlar
- `GET /reports/by-student/{id}`
- `GET /reports/by-test/{id}`
- `GET /reports/latest`
- `GET /reports/summary`

---

## 🔐 Güvenlik ve Ağ

- Tüm iletişim HTTPS üzerinden (TLS 1.2+)
- JWT tabanlı kimlik doğrulama
- Rol tabanlı erişim kontrolü (öğretmen / veli)
- Google Cloud Firewall: sadece 443 (HTTPS) ve 22 (SSH) açık
- Veritabanı sadece backend VM’den erişilebilir (VPC içinde)

---


## ✅ Veritabanı Şeması (PostgreSQL)

<img width="1314" height="695" alt="postgres - public - students" src="https://github.com/user-attachments/assets/faf574a1-305d-4360-9b59-99cd17aa80a3" />

---
## 📦 Kurulum

---
## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.







