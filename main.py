"""
DriveRose - Arac Paylasim Sistemi
==================================
Calistirmak icin:
    python main.py

Gereksinim: Sadece Python 3.9+ (sqlite3 ve tkinter standart kutuphanede dahil)
pip install gerekmez!
"""

import sys
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        from database import create_tables
        create_tables()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Hata", f"Veritabanı başlatılamadı:\n\n{e}")
        sys.exit(1)

    from gui.giris import GirisEkrani
    GirisEkrani().mainloop()

if __name__ == "__main__":
    main()
