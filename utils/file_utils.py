import json
import os

DATA_PATH = "data/iscritti.json"

def carica_dati():
    if not os.path.exists(DATA_PATH):
        return {"lista_principale": []}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_PATH, "w") as f:
        json.dump(dati, f, indent=4)
