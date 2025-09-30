from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PASSWORD = "adminpass"

liste = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/lista')
def lista():
    with open(os.path.join(DATA_DIR, 'iscritti.json')) as f:
        iscritti = json.load(f)
    with open(os.path.join(DATA_DIR, 'Lista_CWL.txt')) as f:
        lista_txt = f.read()
    return render_template('lista.html', iscritti=iscritti, lista_txt=lista_txt)

@app.route('/gestione', methods=['GET', 'POST'])
def gestione():
    global liste
    if request.method == 'POST':
        nome_lista = request.form['nome_lista']
        max_player = int(request.form['max_player'])
        liste[nome_lista] = {'max': max_player, 'players': []}
    return render_template('gestione_liste.html', liste=liste)

@app.route('/sposta', methods=['POST'])
def sposta():
    da = request.form['da']
    a = request.form['a']
    player = request.form['player']
    if player in liste[da]['players'] and len(liste[a]['players']) < liste[a]['max']:
        liste[da]['players'].remove(player)
        liste[a]['players'].append(player)
    return redirect(url_for('gestione'))

@app.route('/finale')
def finale():
    finale_txt = ""
    for nome, info in liste.items():
        finale_txt += f"{nome}:\n" + "\n".join(info['players']) + "\n\n"
    with open(os.path.join(DATA_DIR, 'lista_finale.txt'), 'w') as f:
        f.write(finale_txt)
    return render_template('finale.html', finale=finale_txt)

if __name__ == '__main__':
    app.run(debug=True)
