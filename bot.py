import os
from telegram import Update
from telegram import ForceReply

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

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

from handlers.start import start
from handlers.listaIscritti import mostra_lista
from handlers.esporta import esporta_json
from dotenv import load_dotenv
load_dotenv(dotenv_path="config.env")

load_dotenv()

# Leggi il token dal sistema
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Crea l'applicazione
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Conversazione per iscrizione
conv_iscrizione = ConversationHandler(
    entry_points=[CommandHandler("iscrivimi", start_iscrizione)],
    states={
        NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nome)],
        SELEZIONE: [CallbackQueryHandler(seleziona_player)],
    },
    fallbacks=[CommandHandler("annulla", annulla)],
)

# Conversazione per eliminazione
conv_elimina = ConversationHandler(
    entry_points=[CommandHandler("elimina_iscrizione", elimina_iscrizione_interattiva)],
    states={
        ELIMINA_SCELTA: [CallbackQueryHandler(conferma_eliminazione)],
    },
    fallbacks=[CommandHandler("annulla", annulla)],
)

# Comandi statici
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("lista", mostra_lista))
app.add_handler(CommandHandler("esporta", esporta_json))
app.add_handler(CommandHandler("annulla", annulla))

# Conversazioni
app.add_handler(conv_iscrizione)
app.add_handler(conv_elimina)

# Avvio
if __name__ == "__main__":
    print("🤖 Bot avviato... in ascolto su Telegram!")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("🛑 Bot interrotto manualmente.")

