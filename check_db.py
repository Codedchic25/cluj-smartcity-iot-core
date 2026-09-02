# check_db.py
import sqlite3
from pathlib import Path

db_path = Path("app.db")
print(f"🔍 Verificăm fișierul: {db_path.absolute()}")
print(f"📏 Dimensiune fișier: {db_path.stat().st_size / 1024:.2f} KB\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Extragere listă tabele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabele = [row[0] for row in cursor.fetchall()]
print(f"📦 Tabele identificate în baza de date: {tabele}")

# 2. Inspectare tabelă sensors (dacă există)
if "sensors" in tabele:
    cursor.execute("PRAGMA table_info(sensors);")
    coloane_sensors = [row[1] for row in cursor.fetchall()]
    print(f"📋 Coloane în tabela 'sensors': {coloane_sensors}")

    cursor.execute("SELECT COUNT(*) FROM sensors;")
    randuri_sensors = cursor.fetchone()[0]
    print(f"🔢 Număr de rânduri în tabela 'sensors': {randuri_sensors}")

    if randuri_sensors > 0:
        cursor.execute("SELECT * FROM sensors LIMIT 3;")
        print(f"👀 Primele rânduri din 'sensors': {cursor.fetchall()}")
else:
    print("❌ Tabela 'sensors' NU există în acest fișier app.db!")

# 3. Inspectare tabelă city_stats (dacă există)
if "city_stats" in tabele:
    cursor.execute("SELECT COUNT(*) FROM city_stats;")
    print(f"🔢 Număr de rânduri în tabela 'city_stats': {cursor.fetchone()[0]}")

conn.close()
