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
    for i, player in enumerate(lista, start=1):
        nome = player.get("nome_player", "Sconosciuto")
        th = player.get("th", "TH?")
        testo += f"{i}. 👤 *{nome}* | {th} \n"

    await update.message.reply_markdown(testo)
