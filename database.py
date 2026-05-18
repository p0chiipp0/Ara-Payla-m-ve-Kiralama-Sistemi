import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "driverose.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Kullanici (
            kullanici_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            ad            TEXT NOT NULL,
            soyad         TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            sifre_hash    TEXT NOT NULL,
            telefon       TEXT,
            tc_no         TEXT NOT NULL UNIQUE,
            ehliyet_no    TEXT NOT NULL UNIQUE,
            rol           TEXT NOT NULL DEFAULT 'kullanici',
            kayit_tarihi  TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS Kategori (
            kategori_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            ad           TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Arac (
            arac_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            marka          TEXT NOT NULL,
            model          TEXT NOT NULL,
            yil            INTEGER,
            kilometre      INTEGER DEFAULT 0,
            yakit_tipi     TEXT,
            vites_tipi     TEXT,
            gunluk_fiyat   REAL NOT NULL,
            musait_mi      INTEGER DEFAULT 1,
            kategori_id    INTEGER REFERENCES Kategori(kategori_id),
            aciklama       TEXT,
            eklenme_tarihi TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS AracFoto (
            foto_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            arac_id   INTEGER REFERENCES Arac(arac_id) ON DELETE CASCADE,
            foto_yolu TEXT NOT NULL,
            ana_foto  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Kiralama (
            kiralama_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id   INTEGER REFERENCES Kullanici(kullanici_id),
            arac_id        INTEGER REFERENCES Arac(arac_id),
            baslangic_saat TEXT NOT NULL,
            bitis_saat     TEXT NOT NULL,
            gun_sayisi     INTEGER NOT NULL,
            toplam_fiyat   REAL NOT NULL,
            durum          TEXT DEFAULT 'aktif'
        );
    """)

    # Varsayılan admin
    cur.execute("SELECT COUNT(*) FROM Kullanici WHERE rol='admin'")
    if cur.fetchone()[0] == 0:
        import hashlib
        h = hashlib.sha256(b"admin123").hexdigest()
        cur.execute("""
            INSERT INTO Kullanici (ad, soyad, email, sifre_hash, tc_no, ehliyet_no, rol)
            VALUES ('Admin','DriveRose','admin@driverose.com',?,?,?,'admin')
        """, (h, "00000000000", "ADMIN000"))

    # Örnek kategoriler
    for kat in ["Sedan", "SUV", "Hatchback", "Elektrikli", "Cabrio"]:
        cur.execute("INSERT OR IGNORE INTO Kategori (ad) VALUES (?)", (kat,))

    # Örnek araçlar (ilk kurulumda)
    cur.execute("SELECT COUNT(*) FROM Arac")
    if cur.fetchone()[0] == 0:
        araçlar = [
            ("Toyota",     "Corolla 2023", 2023, 45000, "Benzin",   "Otomatik", 850.0,  1, 1),
            ("Renault",    "Clio 2022",    2022, 62000, "Dizel",    "Manuel",   650.0,  1, 3),
            ("Tesla",      "Model 3 2024", 2024, 18000, "Elektrik", "Otomatik", 1400.0, 1, 4),
            ("Volkswagen", "Polo 2021",    2021, 55000, "Benzin",   "Manuel",   700.0,  1, 3),
            ("BMW",        "X3 2022",      2022, 38000, "Dizel",    "Otomatik", 1200.0, 1, 2),
        ]
        cur.executemany("""
            INSERT INTO Arac (marka, model, yil, kilometre, yakit_tipi,
                              vites_tipi, gunluk_fiyat, musait_mi, kategori_id)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, araçlar)

    conn.commit()
    conn.close()
    print(f"Veritabanı hazır: {DB_PATH}")
