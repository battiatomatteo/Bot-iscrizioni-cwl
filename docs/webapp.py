from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os, json

# 📁 Percorsi dinamici
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR.parent / "data"

# 🐞 Debug percorsi
print("📁 STATIC_DIR:", STATIC_DIR)
print("📁 TEMPLATES_DIR:", TEMPLATES_DIR)
print("📁 DATA_DIR:", DATA_DIR)

# 🔐 Configurazione
PASSWORD = "adminpass"
liste = {}

# 🚀 FastAPI setup
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

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request):
    with open(DATA_DIR / "iscritti.json", encoding="utf-8") as f:
        iscritti = json.load(f)
    with open(DATA_DIR / "Lista_CWL.txt", encoding="utf-8") as f:
        lista_txt = f.read()
    return templates.TemplateResponse("lista.html", {"request": request, "iscritti": iscritti, "lista_txt": lista_txt})

@app.get("/gestione", response_class=HTMLResponse)
def gestione(request: Request):
    path_salvataggio = DATA_DIR / "liste_salvate.txt"
    if path_salvataggio.exists():
        with open(path_salvataggio, encoding="utf-8") as f:
            blocchi = f.read().strip().split("\n\n")
            for blocco in blocchi:
                righe = blocco.strip().split("\n")
                if righe:
                    intestazione = righe[0]
                    nome = intestazione.split(" (max:")[0]
                    max_player = int(intestazione.split("max: ")[1].replace("):", ""))
                    players = righe[1:]
                    liste[nome] = {"max": max_player, "players": players}
    return templates.TemplateResponse("gestione_liste.html", {"request": request, "liste": liste, "mancanti": []})

@app.post("/crea_lista", response_class=HTMLResponse)
def crea_lista(request: Request, nome_lista: str = Form(...), max_player: int = Form(...)):
    liste[nome_lista] = {"max": max_player, "players": []}
    return RedirectResponse("/gestione", status_code=302)

@app.post("/sposta", response_class=HTMLResponse)
def sposta_player(request: Request, player: str = Form(...), da: str = Form(...), a: str = Form(...)):
    messaggi = {}

    # Rimuovi da lista di partenza (match parziale e case-insensitive)
    originali = liste.get(da, {}).get("players", [])
    for p in originali:
        if p.strip().lower() == player.strip().lower():
            liste[da]["players"].remove(p)
            break


    # Aggiungi a lista di destinazione
    liste.setdefault(a, {"max": 0, "players": []})
    liste[a]["players"].append(player)

    # Calcola messaggi dinamici
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
        "mancanti": [],
        "messaggi": messaggi
    })

@app.post("/genera_liste", response_class=HTMLResponse)
def genera_liste(request: Request):
    try:
        with open(DATA_DIR / "iscritti.json", encoding="utf-8") as f:
            data = json.load(f)
            iscritti = data.get("lista_principale", [])
    except Exception:
        iscritti = []

    def estrai_th(player):
        th_str = player.get("th", "")
        try:
            return int(str(th_str).replace("TH", "").strip())
        except:
            return 0

    validi = [p for p in iscritti if isinstance(p, dict) and not p.get("riserva", False)]
    riserve = [p["nome_player"] for p in iscritti if isinstance(p, dict) and p.get("riserva", False)]
    ordinati = sorted(validi, key=estrai_th, reverse=True)

    mancanti = riserve.copy()
    idx = 0

    for nome, info in liste.items():
        max_p = info["max"]
        info["players"] = []
        while len(info["players"]) < max_p and idx < len(ordinati):
            info["players"].append(ordinati[idx]["nome_player"])
            idx += 1

    mancanti += [p["nome_player"] for p in ordinati[idx:]]

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": mancanti
    })

@app.post("/salva_liste", response_class=HTMLResponse)
def salva_liste(request: Request):
    if not liste:
        return templates.TemplateResponse("gestione_liste.html", {
            "request": request,
            "liste": liste,
            "mancanti": []
        })

    output = ""
    for nome, info in liste.items():
        output += f"{nome} (max: {info['max']}):\n"
        output += "\n".join(info["players"]) + "\n\n"

    with open(DATA_DIR / "liste_salvate.txt", "w", encoding="utf-8") as f:
        f.write(output)

    return templates.TemplateResponse("gestione_liste.html", {
        "request": request,
        "liste": liste,
        "mancanti": []
    })

@app.post("/reset_liste", response_class=HTMLResponse)
def reset_liste(request: Request):
    liste.clear()
    path_salvataggio = DATA_DIR / "liste_salvate.txt"
    if path_salvataggio.exists():
        path_salvataggio.unlink()
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
    return templates.TemplateResponse("finale.html", {"request": request, "finale": finale_txt})
