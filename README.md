
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
└── results
└── report

````

---

## 📑 API Endpointleri (FastAPI)

### ✅ Kimlik Doğrulama (Authentication)

* `POST /signup` – Kullanıcı kaydı (öğretmen/veli)
* `POST /login` – Giriş yap, JWT token al
* `GET /user/me` – Mevcut kullanıcı bilgileri (token ile)

---

### 👨‍🎓 Öğrenci İşlemleri

* `GET /students` – Tüm öğrencileri getir (öğretmen)
* `POST /students` – Yeni öğrenci oluştur
* `GET /students/{student_id}` – Belirli öğrenci bilgisi
* `GET /students/{student_id}/results-summary` – Öğrenciye ait test özetleri
* `GET /students/{student_id}/results-detailed` – Öğrenciye ait test detayları

---

### 🧪 Test İşlemleri

* `GET /tests/` – Tüm testleri getir
* `POST /tests/` – Yeni test oluştur
* `GET /tests/{test_id}` – Belirli test bilgisi
* `POST /create_test` – AI ile test üret (Gemini)
* `POST /create_test_result_and_report` – Test çözümü sonrası sonuç ve rapor oluştur

---

### 📊 Test Sonuçları

* `GET /results/` – Tüm sonuçlar
* `GET /results/by-student/{student_id}` – Öğrencinin tüm sonuçları
* `GET /results/by-test/{test_id}` – Teste ait tüm sonuçlar
* `GET /results/latest` – En son test sonucu
* `GET /results/summary` – Genel sonuç özeti

---

### 📈 Raporlar

* `GET /reports/` – Tüm raporları getir
* `GET /reports/by-result/{result_id}` – Belirli sonuca ait rapor
* `GET /reports/latest` – En son oluşturulan rapor

---

### 🔊 Hikaye ve Seslendirme (AI Tabanlı)

* `POST /story/` – Masal/hikaye üret (Gemini API)
* `POST /tts/` – Metni seslendir (Google Cloud TTS)

---


## 🔐 Güvenlik ve Ağ

- Tüm iletişim HTTPS üzerinden (TLS 1.2+)
- JWT tabanlı kimlik doğrulama
- Rol tabanlı erişim kontrolü (öğretmen / veli)
- Google Cloud Firewall: sadece 443 (HTTPS) ve 22 (SSH) açık
- Veritabanı sadece backend VM’den erişilebilir (VPC içinde)

---


## ✅ Veritabanı Şeması (PostgreSQL)

<img width="1733" height="461" alt="postgres - public" src="https://github.com/user-attachments/assets/6c80206c-c13f-42e9-a4d7-fb6b68aaa2a1" />


---
## 📦 Kurulum

---
## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.







