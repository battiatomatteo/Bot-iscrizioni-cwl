from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

# 📁 Percorsi
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR.parent / "data"

# 🔐 Config
PASSWORD = "adminpass"
liste = {}

# 🚀 FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, password: str = Form(...)):
    if password == PASSWORD:
        response = RedirectResponse("/home", status_code=302)
        response.set_cookie("auth", "true")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Password errata"})

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    if request.cookies.get("auth") != "true":
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/lista", response_class=HTMLResponse, name="lista")
def lista(request: Request):
    try:
        with open(DATA_DIR / "iscritti.json", encoding="utf-8") as f:
            iscritti = json.load(f)
    except:
        iscritti = {}

    try:
        with open(DATA_DIR / "Lista_CWL.txt", encoding="utf-8") as f:
            lista_txt = f.read()
    except:
        lista_txt = ""

    return templates.TemplateResponse("lista.html", {
        "request": request,
        "iscritti": iscritti,
        "lista_txt": lista_txt
    })

@app.get("/gestione", response_class=HTMLResponse)
def gestione(request: Request):
    path = DATA_DIR / "liste_salvate.txt"
    tutti_player = []

    # Carica da file solo se liste è vuoto
    if not liste and path.exists():
        with open(path, encoding="utf-8") as f:
            blocchi = f.read().strip().split("\n\n")
            for blocco in blocchi:
                righe = blocco.strip().split("\n")
                if righe:
                    intestazione = righe[0]
                    nome = intestazione.split(" (max:")[0]
                    max_player = int(intestazione.split("max: ")[1].replace("):", ""))
                    players = righe[1:]
                    liste[nome] = {"max": max_player, "players": players}
                    tutti_player.extend(players)

    # Ricostruzione lista mancanti
    if "Mancanti" in liste:
        liste["Mancanti"]["players"] = []

    mancanti = []
    try:
        with open(DATA_DIR / "iscritti.json", encoding="utf-8") as f:
            iscritti = json.load(f).get("lista_principale", [])
    except:
        iscritti = []

    def estrai_th(p): return int(str(p.get("th", "")).replace("TH", "").strip() or 0)

    for p in iscritti:
        nome_th = f"{p['nome_player']} (TH{estrai_th(p)})"
        if nome_th not in [x for sublist in [info["players"] for info in liste.values()] for x in sublist]:
            mancanti.append(nome_th)

    liste["Mancanti"] = {"max": 999, "players": mancanti}


    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": mancanti,
        "messaggi": {},
        "conferma": None
    })


@app.post("/crea_lista", response_class=HTMLResponse)
def crea_lista(request: Request, nome_lista: str = Form(...), max_player: int = Form(...)):
    liste[nome_lista] = {"max": max_player, "players": []}
    return RedirectResponse("/gestione", status_code=302)

@app.post("/genera_liste", response_class=HTMLResponse)
def genera_liste(request: Request):
    try:
        with open(DATA_DIR / "iscritti.json", encoding="utf-8") as f:
            iscritti = json.load(f).get("lista_principale", [])
    except:
        iscritti = []

    def estrai_th(p):
        try:
            return int(str(p.get("th", "")).replace("TH", "").strip())
        except:
            return 0

    # Separazione tra validi e riserve
    validi = [p for p in iscritti if not p.get("riserva", False)]
    riserve = [f"{p['nome_player']} (TH{estrai_th(p)})" for p in iscritti if p.get("riserva", False)]
    ordinati = sorted(validi, key=estrai_th, reverse=True)

    # Svuota tutte le liste prima di riempirle
    for nome in liste:
        liste[nome]["players"] = []

    # Assegna i player ordinati alle liste (escludendo Mancanti)
    idx = 0
    for nome, info in liste.items():
        if nome == "Mancanti":
            continue
        max_p = info["max"]
        while len(info["players"]) < max_p and idx < len(ordinati):
            p = ordinati[idx]
            player_str = f"{p['nome_player']} (TH{estrai_th(p)})"
            info["players"].append(player_str)
            idx += 1

    # Ricostruzione Mancanti da riserve + non assegnati
    mancanti = riserve.copy()
    mancanti += [f"{p['nome_player']} (TH{estrai_th(p)})" for p in ordinati[idx:]]

    # Sovrascrivi completamente la lista Mancanti
    liste["Mancanti"] = {"max": 999, "players": mancanti}

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": mancanti,
        "messaggi": {},
        "conferma": "✅ Distribuzione completata"
    })


@app.post("/sposta", response_class=HTMLResponse)
def sposta_player(request: Request, player: str = Form(...), da: str = Form(...), a: str = Form(...)):
    messaggi = {}

    for p in liste.get(da, {}).get("players", []):
        if p.strip().lower().startswith(player.strip().lower()):
            liste[da]["players"].remove(p)
            break

    liste.setdefault(a, {"max": 0, "players": []})
    liste[a]["players"].append(player)

    for nome, info in liste.items():
        attuali = len(info["players"])
        massimo = info["max"]
        if attuali < massimo:
            messaggi[nome] = f"⚠️ Mancano {massimo - attuali} player"
        elif attuali > massimo:
            messaggi[nome] = f"⚠️ Ci sono {attuali - massimo} player in più"
        else:
            messaggi[nome] = "✅ Lista completa"

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": liste.get("Mancanti", []),
        "messaggi": messaggi,
        "conferma": f"✅ Player '{player}' spostato da '{da}' a '{a}'"
    })

@app.post("/salva_liste", response_class=HTMLResponse)
def salva_liste(request: Request):
    output = ""
    for nome, info in liste.items():
        output += f"{nome} (max: {info['max']}):\n"
        output += "\n".join(info["players"]) + "\n\n"

    with open(DATA_DIR / "liste_salvate.txt", "w", encoding="utf-8") as f:
        f.write(output)

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": liste.get("Mancanti", []),
        "messaggi": {},
        "conferma": "✅ Liste salvate correttamente"
    })

@app.post("/reset_liste", response_class=HTMLResponse)
def reset_liste(request: Request):
    liste.clear()
    path = DATA_DIR / "liste_salvate.txt"
    if path.exists():
        path.unlink()
    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": {},
        "mancanti": [],
        "messaggi": {},
        "conferma": "🔄 Tutte le liste sono state resettate"
    })

@app.get("/finale", response_class=HTMLResponse)
def finale(request: Request):
    finale_txt = ""
    for nome, info in liste.items():
        finale_txt += f"{nome}:\n" + "\n".join(info["players"]) + "\n\n"

    with open(DATA_DIR / "lista_finale.txt", "w", encoding="utf-8") as f:
        f.write(finale_txt)

    return templates.TemplateResponse("finale.html", {
        "request": request,
        "finale": finale_txt
    })
