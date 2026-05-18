import os
from database import get_connection

class Arac:
    def __init__(self, arac_id=None, marka='', model='', yil=None,
                 kilometre=0, yakit_tipi='', vites_tipi='',
                 gunluk_fiyat=0.0, musait_mi=True,
                 aciklama='', foto_yolu=None):
        self.arac_id      = arac_id
        self.marka        = marka
        self.model        = model
        self.yil          = yil
        self.kilometre    = kilometre
        self.yakit_tipi   = yakit_tipi
        self.vites_tipi   = vites_tipi
        self.gunluk_fiyat = gunluk_fiyat
        self.musait_mi    = musait_mi
        self.aciklama     = aciklama
        self.foto_yolu    = foto_yolu

    @staticmethod
    def _yolu_duzelt(eski_yol):
        """
        Veritabanındaki eski ve bozuk 'Mutlak Yolu' (Absolute Path)
        o anki bilgisayarın dizinine göre anında onarır.
        """
        if not eski_yol:
            return None
            
        parts = eski_yol.replace("\\", "/").split("/")
        
        if "assets" in parts:
            idx = parts.index("assets")
            rel_path_parts = parts[idx:]
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_dir, *rel_path_parts)
        
        return eski_yol

    def kaydet(self):
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO Arac (marka, model, yil, kilometre, yakit_tipi,
                              vites_tipi, gunluk_fiyat, musait_mi, aciklama)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (self.marka, self.model, self.yil, self.kilometre,
              self.yakit_tipi, self.vites_tipi, self.gunluk_fiyat,
              int(self.musait_mi), self.aciklama))
        self.arac_id = cur.lastrowid
        conn.commit()
        conn.close()
        return self.arac_id

    def guncelle(self):
        conn = get_connection()
        conn.execute("""
            UPDATE Arac SET marka=?, model=?, yil=?, kilometre=?,
            yakit_tipi=?, vites_tipi=?, gunluk_fiyat=?,
            aciklama=? WHERE arac_id=?
        """, (self.marka, self.model, self.yil, self.kilometre,
              self.yakit_tipi, self.vites_tipi, self.gunluk_fiyat,
              self.aciklama, self.arac_id))
        conn.commit()
        conn.close()

    def foto_ekle(self, foto_yolu: str, ana_foto: bool = False):
        conn = get_connection()
        if ana_foto:
            conn.execute("UPDATE AracFoto SET ana_foto=0 WHERE arac_id=?",
                         (self.arac_id,))
        conn.execute("INSERT INTO AracFoto (arac_id, foto_yolu, ana_foto) VALUES (?,?,?)",
                     (self.arac_id, foto_yolu, int(ana_foto)))
        conn.commit()
        conn.close()

    @staticmethod
    def kiralama_gecmisi_var_mi(arac_id: int):
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) FROM Kiralama WHERE arac_id=?", (arac_id,)).fetchone()
        conn.close()
        return row[0] > 0

    @staticmethod
    def hepsini_getir(sadece_musait=False):
        conn  = get_connection()
        query = """
            SELECT a.arac_id, a.marka, a.model, a.yil, a.kilometre,
                   a.yakit_tipi, a.vites_tipi, a.gunluk_fiyat,
                   a.musait_mi, a.aciklama,
                   (SELECT foto_yolu FROM AracFoto WHERE arac_id = a.arac_id ORDER BY ana_foto DESC LIMIT 1) AS foto_yolu
            FROM Arac a
        """
        if sadece_musait:
            query += " WHERE a.musait_mi=1"
        query += " ORDER BY a.marka, a.model"
        rows = conn.execute(query).fetchall()
        conn.close()
        
        sonuclar = []
        for r in rows:
            d = dict(r)
            d["foto_yolu"] = Arac._yolu_duzelt(d["foto_yolu"])
            sonuclar.append(d)
        return sonuclar

    @staticmethod
    def id_ile_getir(arac_id: int):
        conn = get_connection()
        row  = conn.execute("""
            SELECT a.*,
                   (SELECT foto_yolu FROM AracFoto WHERE arac_id = a.arac_id ORDER BY ana_foto DESC LIMIT 1) AS foto_yolu
            FROM Arac a
            WHERE a.arac_id=?
        """, (arac_id,)).fetchone()
        conn.close()
        if row:
            return Arac(
                arac_id=row["arac_id"], marka=row["marka"], model=row["model"],
                yil=row["yil"], kilometre=row["kilometre"],
                yakit_tipi=row["yakit_tipi"], vites_tipi=row["vites_tipi"],
                gunluk_fiyat=float(row["gunluk_fiyat"]),
                musait_mi=bool(row["musait_mi"]),
                aciklama=row["aciklama"] or "",
                foto_yolu=Arac._yolu_duzelt(row["foto_yolu"]) 
            )
        return None

    @staticmethod
    def sil(arac_id: int):
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = OFF")
        try:
            conn.execute("DELETE FROM Kiralama WHERE arac_id=?", (arac_id,))
            conn.execute("DELETE FROM AracFoto WHERE arac_id=?", (arac_id,))
            conn.execute("DELETE FROM Arac WHERE arac_id=?", (arac_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()