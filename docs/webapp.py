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

def get_iscritti_stats():
    path = DATA_DIR / "iscritti.json"
    try:
        with open(path, encoding="utf-8") as f:
            iscritti = json.load(f).get("lista_principale", [])
    except:
        iscritti = []

    totale = len(iscritti)
    riserve = 0
    th_counter = {}

    for p in iscritti:
        th = str(p.get("th", "")).replace("TH", "").strip()
        th_counter[th] = th_counter.get(th, 0) + 1
        if p.get("riserva", False):
            riserve += 1

    return {
        "totale_iscritti": totale,
        "riserve_count": riserve,
        "th_counter": th_counter
    }

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
                    if "max: " in intestazione:
                        try:
                            nome = intestazione.split(" (max:")[0]
                            max_player = int(intestazione.split("max: ")[1].replace("):", ""))
                            players = righe[1:]
                            liste[nome] = {"max": max_player, "players": players}
                            tutti_player.extend(players)
                        except Exception as e:
                            print(f"❌ Errore parsing lista '{intestazione}': {e}")
                    else:
                        print(f"⚠️ Intestazione non valida: {intestazione}")

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

    # Riepilogo iscritti
    stats = get_iscritti_stats()

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": mancanti,
        "messaggi": {},
        "conferma": None,
        "totale_iscritti": stats["totale_iscritti"],
        "riserve_count": stats["riserve_count"],
        "th_counter": stats["th_counter"]
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

    validi = [p for p in iscritti if not p.get("riserva", False)]
    riserve = [f"{p['nome_player']} (TH{estrai_th(p)})" for p in iscritti if p.get("riserva", False)]
    ordinati = sorted(validi, key=estrai_th, reverse=True)

    for nome in liste:
        liste[nome]["players"] = []

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

    mancanti = riserve.copy()
    mancanti += [f"{p['nome_player']} (TH{estrai_th(p)})" for p in ordinati[idx:]]
    liste["Mancanti"] = {"max": 999, "players": mancanti}

    stats = get_iscritti_stats()

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": mancanti,
        "messaggi": {},
        "conferma": "✅ Distribuzione completata",
        "totale_iscritti": stats["totale_iscritti"],
        "riserve_count": stats["riserve_count"],
        "th_counter": stats["th_counter"]
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
    path = DATA_DIR / "liste_salvate.txt"
    with open(path, "w", encoding="utf-8") as f:
        for nome, info in liste.items():
            f.write(f"{nome} (max: {info['max']}):\n")
            for player in info["players"]:
                f.write(f"{player}\n")
            f.write("\n")

    stats = get_iscritti_stats()

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": liste.get("Mancanti", {}).get("players", []),
        "messaggi": {},
        "conferma": "💾 Liste salvate correttamente",
        "totale_iscritti": stats["totale_iscritti"],
        "riserve_count": stats["riserve_count"],
        "th_counter": stats["th_counter"]
    })


@app.post("/reset_liste", response_class=HTMLResponse)
def reset_liste(request: Request):
    liste.clear()
    path = DATA_DIR / "liste_salvate.txt"
    if path.exists():
        path.unlink()

    stats = get_iscritti_stats()

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": {},
        "mancanti": [],
        "messaggi": {},
        "conferma": "🔄 Tutte le liste sono state resettate",
        "totale_iscritti": stats["totale_iscritti"],
        "riserve_count": stats["riserve_count"],
        "th_counter": stats["th_counter"]
    })

from fastapi.responses import FileResponse

@app.get("/download_finale")
def download_finale():
    finale_path = Path("static") / "lista_finale.txt"
    if not finale_path.exists():
        return HTMLResponse("<h3>⚠️ Il file lista_finale.txt non esiste.</h3>", status_code=404)
    return FileResponse(finale_path, media_type="text/plain", filename="lista_finale.txt")


@app.get("/finale", response_class=HTMLResponse)
def finale(request: Request):
    path = DATA_DIR / "liste_salvate.txt"
    finale_path = Path("static") / "lista_finale.txt"
    finale_path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        return HTMLResponse("<h3>⚠️ Nessuna lista salvata da esportare.</h3>", status_code=404)

    with open(path, encoding="utf-8") as f:
        blocchi = f.read().strip().split("\n\n")

    contenuto_finale = []
    for blocco in blocchi:
        righe = blocco.strip().split("\n")
        if righe:
            intestazione = righe[0]
            contenuto_finale.append("════════════════════════════════════")
            contenuto_finale.append(intestazione)
            contenuto_finale.extend(righe[1:])
            contenuto_finale.append("")  # spazio tra blocchi

    with open(finale_path, "w", encoding="utf-8") as f:
        f.write("\n".join(contenuto_finale))

    return templates.TemplateResponse("finale.html", {
        "request": request,
        "contenuto": "\n".join(contenuto_finale)
    })

