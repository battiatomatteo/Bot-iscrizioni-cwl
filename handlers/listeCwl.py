import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import carica_dati

ORDINE_LEGHE = [
    "Champion League III",
    "Champion League II",
    "Master League III",
    "Master League II",
    "Master League I",
    "Crystal League II",
    "Crystal League I"
]

async def genera_txt_cwl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dati = carica_dati()
    lista = dati.get("lista_principale", [])

    # Raggruppa per lega + lista separata per chi non ha lega
    leghe = {lega: [] for lega in ORDINE_LEGHE}
    senza_lega = []

    for player in lista:
        lega = player.get("last_cwl_league")
        if lega in leghe:
            leghe[lega].append(player)
        else:
            senza_lega.append(player)

    # Crea contenuto TXT
    contenuto = "📋 Lista CWL per lega\n\n"
    for lega in ORDINE_LEGHE:
        players = leghe[lega]
        if not players:
            continue

        contenuto += f"🏆 {lega}\n"
        for p in players:
            riga = f"- {p['nome_player']} | {p['th']} | {p['attacker_tag']}\n"
            contenuto += riga
        contenuto += "\n"

    # Aggiungi sezione finale per chi non ha lega
    if senza_lega:
        contenuto += "🚫 Senza lega CWL\n"
        for p in senza_lega:
            riga = f"- {p['nome_player']} | {p['th']} | {p['attacker_tag']}\n"
            contenuto += riga
        contenuto += "\n"

    # Scrivi su file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(contenuto)
        tmp.flush()
        await update.message.reply_document(document=open(tmp.name, "rb"), filename="Lista_CWL.txt")
