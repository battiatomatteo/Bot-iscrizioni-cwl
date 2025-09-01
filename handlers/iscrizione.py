import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from utils.file_utils import carica_dati, salva_dati

NOME, TH, SELEZIONE = range(3)

# Step 1: Inserimento nome
async def start_iscrizione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inserisci il nome del player da iscrivere:")
    return NOME

# Step 2: Selezione TH
async def ricevi_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text

    keyboard = []
    row = []
    for i in range(1, 18):
        row.append(InlineKeyboardButton(f"TH{i}", callback_data=f"TH{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ora seleziona il livello TH:", reply_markup=reply_markup)
    return TH

# Step 3: Ricerca nel database CWL
async def ricevi_th(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    th = query.data
    context.user_data["th"] = th
    nome = context.user_data["nome"]

    try:
        response = requests.get("https://api.warmachine.cc/v1/playerlist")
        response.raise_for_status()
        player_list = response.json()
    except Exception:
        await query.edit_message_text("❌ Errore nel recupero dei dati esterni.")
        return ConversationHandler.END

    # Cerca nomi simili
    matches = [
        p for p in player_list
        if nome.lower() in p["attacker_name"].lower()
    ]

    if not matches:
        await query.edit_message_text(
            f"⚠️ Nessun player trovato con il nome *{nome}*.\n"
            "Controlla la scrittura o contatta un admin."
        )
        return ConversationHandler.END

    if len(matches) == 1:
        return await salva_player(update, context, matches[0])

    # Mostra tastiera con opzioni
    keyboard = []
    row = []
    for player in matches:
        display_name = player["attacker_name"]
        tag = player["attacker_tag"]
        row.append(InlineKeyboardButton(display_name, callback_data=tag))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Seleziona il nome corretto:", reply_markup=reply_markup)
    context.user_data["matches"] = matches
    return SELEZIONE

# Step 4: Selezione finale
async def seleziona_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_tag = query.data
    matches = context.user_data.get("matches", [])
    th = context.user_data["th"]

    player = next((p for p in matches if p["attacker_tag"] == selected_tag), None)
    if not player:
        await query.edit_message_text("❌ Errore nella selezione del player.")
        return ConversationHandler.END

    # Sovrascrivi il nome con quello selezionato
    context.user_data["nome"] = player["attacker_name"]

    return await salva_player(update, context, player)


# Salvataggio finale
async def salva_player(update: Update, context: ContextTypes.DEFAULT_TYPE, player):
    nome = context.user_data["nome"]
    th = context.user_data["th"]
    tag = player["attacker_tag"]

    dati = carica_dati()
    lista = dati.get("lista_principale", [])
    lista.append({
        "nome_player": nome,
        "th": th,
        "attacker_tag": tag
    })
    dati["lista_principale"] = lista
    salva_dati(dati)

    await update.callback_query.message.reply_text(
        f"✅ *Iscrizione completata!*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"🏰 *TH:* {th}\n"
        f"🏷️ *Tag:* `{tag}`\n\n"
        "📌 Il player è stato aggiunto alla lista CWL."
    )
    return ConversationHandler.END

# Annulla iscrizione
async def annulla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iscrizione annullata ❌")
    return ConversationHandler.END
