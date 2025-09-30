from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, json

app = FastAPI()
app.mount("/static", StaticFiles(directory="docs/static"), name="static")
templates = Jinja2Templates(directory="docs/templates")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PASSWORD = "adminpass"
liste = {}

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
    with open(os.path.join(DATA_DIR, "iscritti.json")) as f:
        iscritti = json.load(f)
    with open(os.path.join(DATA_DIR, "Lista_CWL.txt")) as f:
        lista_txt = f.read()
    return templates.TemplateResponse("lista.html", {"request": request, "iscritti": iscritti, "lista_txt": lista_txt})

@app.get("/gestione", response_class=HTMLResponse)
def gestione(request: Request):
    return templates.TemplateResponse("gestione_liste.html", {"request": request, "liste": liste})

@app.post("/crea_lista", response_class=HTMLResponse)
def crea_lista(request: Request, nome_lista: str = Form(...), max_player: int = Form(...)):
    liste[nome_lista] = {"max": max_player, "players": []}
    return RedirectResponse("/gestione", status_code=302)

@app.post("/sposta", response_class=HTMLResponse)
def sposta_player(request: Request, player: str = Form(...), da: str = Form(...), a: str = Form(...)):
    if player in liste.get(da, {}).get("players", []) and len(liste.get(a, {}).get("players", [])) < liste[a]["max"]:
        liste[da]["players"].remove(player)
        liste[a]["players"].append(player)
    return RedirectResponse("/gestione", status_code=302)

@app.get("/finale", response_class=HTMLResponse)
def finale(request: Request):
    finale_txt = ""
    for nome, info in liste.items():
        finale_txt += f"{nome}:\n" + "\n".join(info["players"]) + "\n\n"
    with open(os.path.join(DATA_DIR, "lista_finale.txt"), "w") as f:
        f.write(finale_txt)
    return templates.TemplateResponse("finale.html", {"request": request, "finale": finale_txt})
