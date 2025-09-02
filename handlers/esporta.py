from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import carica_dati
import json

async def esporta_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dati = carica_dati()
    json_text = json.dumps(dati, indent=2)

    await update.message.reply_document(
        document=bytes(json_text, encoding='utf-8'),
        filename="iscritti.json",
        caption="📦 Ecco il file JSON con gli iscritti CWL."
    )
