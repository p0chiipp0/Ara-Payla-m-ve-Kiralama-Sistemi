from datetime import datetime, timedelta
from database import get_connection

class Kiralama:
    def __init__(self, kiralama_id=None, kullanici_id=None, arac_id=None,
                 baslangic_saat=None, bitis_saat=None,
                 gun_sayisi=1, toplam_fiyat=0.0, durum='aktif'):
        self.kiralama_id   = kiralama_id
        self.kullanici_id  = kullanici_id
        self.arac_id       = arac_id
        self.baslangic_saat = baslangic_saat or datetime.now()
        self.bitis_saat    = bitis_saat
        self.gun_sayisi    = gun_sayisi
        self.toplam_fiyat  = toplam_fiyat
        self.durum         = durum

    @staticmethod
    def fiyat_hesapla(gunluk_fiyat: float, gun_sayisi: int) -> float:
        return round(gunluk_fiyat * gun_sayisi, 2)

    def kiralama_baslat(self):
        self.baslangic_saat = datetime.now()
        self.bitis_saat     = self.baslangic_saat + timedelta(days=self.gun_sayisi)
        bas_str = self.baslangic_saat.strftime("%Y-%m-%d %H:%M:%S")
        bit_str = self.bitis_saat.strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO Kiralama (kullanici_id, arac_id, baslangic_saat,
                                   bitis_saat, gun_sayisi, toplam_fiyat, durum)
            VALUES (?,?,?,?,?,?,'aktif')
        """, (self.kullanici_id, self.arac_id, bas_str, bit_str,
              self.gun_sayisi, self.toplam_fiyat))
        self.kiralama_id = cur.lastrowid
        conn.execute("UPDATE Arac SET musait_mi=0 WHERE arac_id=?", (self.arac_id,))
        conn.commit()
        conn.close()
        return self.kiralama_id

    def kiralama_bitir(self):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        conn.execute("""
            UPDATE Kiralama SET durum='tamamlandi', bitis_saat=?
            WHERE kiralama_id=?
        """, (now_str, self.kiralama_id))
        conn.execute("UPDATE Arac SET musait_mi=1 WHERE arac_id=?", (self.arac_id,))
        conn.commit()
        conn.close()
        self.durum = 'tamamlandi'

    @staticmethod
    def tum_kiralamalar():
        conn = get_connection()
        rows = conn.execute("""
            SELECT k.kiralama_id,
                   u.ad||' '||u.soyad  AS kullanici,
                   a.marka||' '||a.model AS arac,
                   k.baslangic_saat, k.bitis_saat,
                   k.gun_sayisi, k.toplam_fiyat, k.durum,
                   k.arac_id
            FROM Kiralama k
            JOIN Kullanici u ON k.kullanici_id = u.kullanici_id
            JOIN Arac a ON k.arac_id = a.arac_id
            ORDER BY k.baslangic_saat DESC
        """).fetchall()
        conn.close()
        return rows

    @staticmethod
    def dashboard_istatistik() -> dict:
        conn  = get_connection()
        stats = {}
        stats['toplam_arac']      = conn.execute("SELECT COUNT(*) FROM Arac").fetchone()[0]
        stats['toplam_kullanici'] = conn.execute("SELECT COUNT(*) FROM Kullanici WHERE rol='kullanici'").fetchone()[0]
        stats['aktif_kiralama']   = conn.execute("SELECT COUNT(*) FROM Kiralama WHERE durum='aktif'").fetchone()[0]
        ay = datetime.now().strftime("%Y-%m")
        row = conn.execute("""
            SELECT IFNULL(SUM(toplam_fiyat),0) FROM Kiralama
            WHERE strftime('%Y-%m', baslangic_saat)=? 
        """, (ay,)).fetchone()
        stats['aylik_gelir'] = float(row[0])
        conn.close()
        return stats