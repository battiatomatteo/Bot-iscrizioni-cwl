import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Importa i tuoi handler personalizzati
from handlers.iscrizione import (
    start_iscrizione,
    ricevi_nome,
    seleziona_player,
    annulla,
    elimina_iscrizione_interattiva,
    conferma_eliminazione,
    NOME,
    SELEZIONE,
    ELIMINA_SCELTA
)
from handlers.listeCwl import genera_txt_cwl
from handlers.start import start
from handlers.listaIscritti import mostra_lista
from handlers.esporta import esporta_json

# 🔐 Carica variabili ambiente
load_dotenv(dotenv_path="config.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🤖 Crea l'applicazione Telegram
application = Application.builder().token(BOT_TOKEN).build()

# 🌐 Crea l'app FastAPI
app = FastAPI()

# 📬 Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

# 🧩 Comando per aprire la Mini App
async def apri_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧩 Apri Mini App", web_app=WebAppInfo(url="https://battiatomatteo.github.io/Bot-iscrizioni-cwl/"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Apri la Mini App per gestire le iscrizioni:", reply_markup=reply_markup)

# 🗂️ Conversazione per iscrizione
conv_iscrizione = ConversationHandler(
    entry_points=[CommandHandler("iscrivimi", start_iscrizione)],
    states={
        NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nome)],
        SELEZIONE: [CallbackQueryHandler(seleziona_player)],
    },
    fallbacks=[CommandHandler("annulla", annulla)],
)

# 🗑️ Conversazione per eliminazione
conv_elimina = ConversationHandler(
    entry_points=[CommandHandler("elimina_iscrizione", elimina_iscrizione_interattiva)],
    states={
        ELIMINA_SCELTA: [CallbackQueryHandler(conferma_eliminazione)],
    },
    fallbacks=[CommandHandler("annulla", annulla)],
)

# 📌 Aggiungi tutti gli handler al bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("lista", mostra_lista))
application.add_handler(CommandHandler("esporta", esporta_json))
application.add_handler(CommandHandler("annulla", annulla))
application.add_handler(CommandHandler("txt_cwl", genera_txt_cwl))
application.add_handler(CommandHandler("app_admin", apri_webapp))
application.add_handler(conv_iscrizione)
application.add_handler(conv_elimina)

# 🚀 Avvio locale con polling (solo per test locali)
if __name__ == "__main__":
    print("🤖 Bot avviato... in ascolto su Telegram!")
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("🛑 Bot interrotto manualmente.")
