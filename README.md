# 🌸 DriveRose - Araç Paylaşım ve Kiralama Sistemi

DriveRose, Python kullanılarak geliştirilmiş, standart kütüphaneler ile çalışan hafif ve kullanıcı dostu bir Masaüstü Araç Kiralama/Paylaşım Otomasyonudur.

Hiçbir harici kütüphaneye (örneğin `pip install ...` gibi) ihtiyaç duymaz. Sadece Python 3.9 veya daha güncel bir sürümün yüklü olması yeterlidir. Veritabanı olarak dahili SQLite kullanmaktadır.

## 🚀 Özellikler

*   **Rol Bazlı Yetkilendirme:** Yönetici (Admin) ve Normal Kullanıcı olmak üzere iki farklı kullanıcı tipi.
*   **Kullanıcı Modülü:**
    *   Kayıt olma ve güvenli giriş yapma işlemleri.
    *   Sistemdeki müsait araçları listeleyebilme ve özelliklerine göre inceleme.
    *   Araç kiralama (tarih ve gün bazlı otomatik fiyat hesaplamaları).
    *   Aktif ve geçmiş kiralama kayıtlarını görüntüleme.
*   **Yönetici (Admin) Modülü:**
    *   Araç filosu yönetimi (Araç ekleme, düzenleme, silme ve kategori atama).
    *   Araçlara fotoğraf yükleme ve vitrin (ana) resmi belirleme.
    *   Sistemde kayıtlı kullanıcıların listesini görüntüleme.
    *   Tüm kiralama hareketlerini (aktif/geçmiş) sistem üzerinden takip edebilme.
*   **Modern Arayüz (GUI):** `tkinter` modülü kullanılarak hazırlanmış, özel tasarım renk paleti ve kart yapıları içeren kullanıcı dostu temiz bir arayüz.
*   **Dahili Veritabanı:** Kurulum gerektirmeyen, güvenilir ve taşınabilir `SQLite3` mimarisi.

## 🛠️ Kurulum ve Çalıştırma

1.  Projeyi bilgisayarınıza indirin veya klonlayın:
    ```bash
    git clone https://github.com/KULLANICI_ADINIZ/driverose.git
    cd driverose
    ```

2.  Projeyi başlatmak için terminal veya komut satırını (CMD/PowerShell) açıp şu komutu çalıştırın:
    ```bash
    python main.py
    ```

> **Not:** Uygulama ilk kez çalıştırıldığında gerekli veritabanı dosyası (`driverose.db`) otomatik olarak oluşturulacak ve sistem test edebilmeniz için örnek araçlar/kategorilerle yüklenecektir.

## 🔑 Varsayılan Giriş Bilgileri

Sisteme yönetici paneline erişmek ve tüm özellikleri incelemek için ilk kurulumda otomatik oluşturulan test hesabını kullanabilirsiniz:

*   **E-posta:** `admin@driverose.com`
*   **Şifre:** `admin123`

## 📁 Proje Mimarisi (Klasör Yapısı)

*   `main.py` : Uygulamanın başlatıldığı ana giriş (entry-point) dosyasıdır.
*   `database.py` : Veritabanı bağlantısı, tabloların oluşturulması ve varsayılan verilerin (admin kullanıcısı, örnek araçlar) veritabanına yazıldığı modüldür.
*   `gui/` : Uygulamanın tüm görsel arayüz kodlarını içerir. (Giriş ekranı, Kayıt ekranı, Admin Paneli, Kullanıcı Paneli ve Tema motoru)
*   `models/` : Veritabanı tabloları ile arayüz arasındaki köprüyü kuran (CRUD işlemleri) nesne yönelimli sınıfları barındırır.
*   `assets/` : Araçlara ait yüklenen görsel ve fotoğrafların barındırıldığı medya dizinidir.
