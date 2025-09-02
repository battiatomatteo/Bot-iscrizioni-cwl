from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder

import os

# Carica il token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Crea l'app Telegram
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Crea l'app FastAPI
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}
