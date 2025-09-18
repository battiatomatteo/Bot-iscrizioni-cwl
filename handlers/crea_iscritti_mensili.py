# crea_iscritti_mensili.py
import json 
import datetime
import os

DATA_FILE = "./data/iscritti.json"
OUTPUT_DIR = "./data/output"


def get_target_filename():
    """
    Calcola il nome del file da creare per il mese corrente.
    """
    today = datetime.date.today()
    file_year, file_month = today.year, today.month

    if today.month == 1:  # caso gennaio → dati da dicembre anno prima
        prev_year, prev_month = today.year - 1, 12
    else:
        prev_year, prev_month = today.year, today.month - 1

    filename = f"iscritti.{file_year}.{file_month:02d}.json"
    return os.path.join(OUTPUT_DIR, filename), (prev_year, prev_month)


def crea_file_iscritti():
    """
    Se il file del mese corrente non esiste, lo crea prendendo i dati
    da ./data/iscritti.json.
    """
    filename, (data_year, data_month) = get_target_filename()

    if os.path.exists(filename):
        return None

    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    lista = data.get("lista_principale", [])

    iscritti = []
    for item in lista:
        item_copy = item.copy()
        item_copy["mese"] = f"{data_year}-{data_month:02d}"
        iscritti.append(item_copy)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(iscritti, f, indent=4, ensure_ascii=False)

    return filename
