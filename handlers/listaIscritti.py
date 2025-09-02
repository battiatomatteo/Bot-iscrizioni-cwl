from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import carica_dati

async def mostra_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dati = carica_dati()
    lista = dati.get("lista_principale", [])

    if not lista:
        await update.message.reply_text("La lista è vuota 🫥")
        return

    testo = "📋 *Lista iscritti CWL:*\n\n"
    for i, p in enumerate(lista, start=1):
        testo += f"{i}. 👤 *{p['nome_player']}* | {p['th']} | `{p['attacker_tag']}`\n"

    await update.message.reply_markdown(testo)
