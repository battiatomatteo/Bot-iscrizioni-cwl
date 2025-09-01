from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
from handlers.iscrizione import (
    start_iscrizione,
    ricevi_nome,
    ricevi_th,
    seleziona_player,
    annulla,
    NOME,
    TH,
    SELEZIONE
)
from config import BOT_TOKEN
from telegram.ext import CallbackQueryHandler
from handlers.listaIscritti import mostra_lista
from handlers.start import start

app = ApplicationBuilder().token(BOT_TOKEN).build()

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("iscrivimi", start_iscrizione)],
    states={
        NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nome)],
        TH: [CallbackQueryHandler(ricevi_th)],
        SELEZIONE: [CallbackQueryHandler(seleziona_player)],
    },
    fallbacks=[CommandHandler("annulla", annulla)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)
app.add_handler(CommandHandler("lista", mostra_lista))

print("Bot avviato... in ascolto su Telegram!")
app.run_polling()

