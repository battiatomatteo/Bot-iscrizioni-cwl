from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio = (
        "👋 *Benvenuto!*\n\n"
        "Con questo bot potrai iscriverti alla prossima *CWL* e gestire i player del clan.\n\n"
        "📌 *Comandi disponibili:*\n"
        "`/start` – Mostra questo messaggio\n"
        "`/iscrivimi` – Iscriviti alla lista CWL inserendo nome e TH\n"
        "`/lista` – Visualizza tutti gli iscritti\n"
        "`/annulla` – Annulla l'iscrizione in corso\n"
        "`/esporta` – Esporta la lista in un file JSON\n"
        "`/elimina_iscrizione` – Elimina l'iscrizione di un tuo account\n\n"
        "🎮 *Buon game!*"
    )

    await update.message.reply_markdown(messaggio)
