from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio = (
        "👋 *Benvenuto!*\n\n"
        "Con questo bot potrai iscriverti alla prossima *CWL* e gestire i player del clan.\n\n"
        "📌 *Comandi disponibili:*\n"
        "`/iscrivimi` – Iscriviti alla lista CWL inserendo nome e TH\n"
        "`/lista` – Visualizza tutti gli iscritti\n"
        "`/annulla` – Annulla l'iscrizione in corso\n"
        "`/start` – Mostra questo messaggio\n\n"
        "🎮 *Buon game!*"
    )

    await update.message.reply_markdown(messaggio)
