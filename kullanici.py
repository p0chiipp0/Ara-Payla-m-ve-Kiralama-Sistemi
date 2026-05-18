import hashlib
from database import get_connection

def sifre_hashle(sifre: str) -> str:
    return hashlib.sha256(sifre.encode()).hexdigest()

class Kullanici:
    def __init__(self, kullanici_id=None, ad='', soyad='', email='',
                 telefon='', tc_no='', ehliyet_no='', rol='kullanici'):
        self.kullanici_id = kullanici_id
        self.ad           = ad
        self.soyad        = soyad
        self.email        = email
        self.telefon      = telefon
        self.tc_no        = tc_no
        self.ehliyet_no   = ehliyet_no
        self.rol          = rol

    @property
    def tam_ad(self):
        return f"{self.ad} {self.soyad}"

    def kaydet(self, sifre: str):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Kullanici (ad, soyad, email, sifre_hash, telefon,
                                       tc_no, ehliyet_no, rol)
                VALUES (?,?,?,?,?,?,?,?)
            """, (self.ad, self.soyad, self.email, sifre_hashle(sifre),
                  self.telefon, self.tc_no, self.ehliyet_no, self.rol))
            self.kullanici_id = cur.lastrowid
            conn.commit()
            conn.close()
            return True, "Kayıt başarılı."
        except Exception as e:
            conn.close()
            if "UNIQUE" in str(e):
                return False, "Bu e-posta, TC no veya ehliyet numarası zaten kayıtlı."
            return False, str(e)

    def bilgileri_guncelle(self, ad=None, soyad=None, email=None, telefon=None):
        if ad:      self.ad      = ad
        if soyad:   self.soyad   = soyad
        if email:   self.email   = email
        if telefon: self.telefon = telefon
        conn = get_connection()
        conn.execute("""
            UPDATE Kullanici SET ad=?, soyad=?, email=?, telefon=?
            WHERE kullanici_id=?
        """, (self.ad, self.soyad, self.email, self.telefon, self.kullanici_id))
        conn.commit()
        conn.close()

    def kiralama_gecmisi(self):
        conn = get_connection()
        rows = conn.execute("""
            SELECT k.kiralama_id, a.marka, a.model, k.baslangic_saat,
                   k.bitis_saat, k.gun_sayisi, k.toplam_fiyat, k.durum
            FROM Kiralama k
            JOIN Arac a ON k.arac_id = a.arac_id
            WHERE k.kullanici_id=?
            ORDER BY k.baslangic_saat DESC
        """, (self.kullanici_id,)).fetchall()
        conn.close()
        return rows

    @staticmethod
    def kiralama_gecmisi_var_mi(kullanici_id: int):
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) FROM Kiralama WHERE kullanici_id=?", (kullanici_id,)).fetchone()
        conn.close()
        return row[0] > 0

    @staticmethod
    def aktif_kiralamasi_var_mi(kullanici_id: int):
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) FROM Kiralama WHERE kullanici_id=? AND durum != 'tamamlandi'", (kullanici_id,)).fetchone()
        conn.close()
        return row[0] > 0

    @staticmethod
    def sil(kullanici_id: int):
        if Kullanici.aktif_kiralamasi_var_mi(kullanici_id):
            raise Exception("Kullanıcının teslim etmediği (aktif) bir aracı var! Lütfen önce kiralamayı bitirin.")

        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = OFF")
        try:
            conn.execute("DELETE FROM Kiralama WHERE kullanici_id=?", (kullanici_id,))
            conn.execute("DELETE FROM Kullanici WHERE kullanici_id=?", (kullanici_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()

    @staticmethod
    def giris_yap(email: str, sifre: str):
        conn = get_connection()
        row  = conn.execute("""
            SELECT kullanici_id, ad, soyad, email, telefon,
                   tc_no, ehliyet_no, rol, sifre_hash
            FROM Kullanici WHERE email=?
        """, (email,)).fetchone()
        conn.close()
        if not row:
            return None, "E-posta bulunamadı."
        if row["sifre_hash"] != sifre_hashle(sifre):
            return None, "Şifre hatalı."
        k = Kullanici(
            kullanici_id=row["kullanici_id"], ad=row["ad"], soyad=row["soyad"],
            email=row["email"], telefon=row["telefon"] or '',
            tc_no=row["tc_no"], ehliyet_no=row["ehliyet_no"], rol=row["rol"]
        )
        return k, "Giriş başarılı."

    @staticmethod
    def hepsini_getir():
        conn = get_connection()
        rows = conn.execute("""
            SELECT kullanici_id, ad, soyad, email, telefon,
                   tc_no, ehliyet_no, rol, kayit_tarihi
            FROM Kullanici WHERE rol='kullanici' ORDER BY ad, soyad
        """).fetchall()
        conn.close()
        return rows