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

NOME, SELEZIONE, ELIMINA_SCELTA = range(3)

# Inizio iscrizione
async def start_iscrizione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inserisci il nome del player da iscrivere:")
    return NOME

# Ricezione nome e ricerca
async def ricevi_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nome"] = update.message.text

    try:
        response = requests.get("https://api.warmachine.cc/v1/playerlist")
        response.raise_for_status()
        player_list = response.json()
    except Exception:
        await update.message.reply_text("❌ Errore nel recupero dei dati esterni.")
        return ConversationHandler.END

    nome = context.user_data["nome"]
    matches = [p for p in player_list if nome.lower() in p["attacker_name"].lower()]

    if not matches:
        await update.message.reply_text(f"⚠️ Nessun player trovato con il nome *{nome}*.")
        return ConversationHandler.END

    if len(matches) == 1:
        return await salva_player(update, context, matches[0])

    keyboard = []
    row = []
    for p in matches:
        row.append(InlineKeyboardButton(p["attacker_name"], callback_data=p["attacker_tag"]))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seleziona il nome corretto:", reply_markup=reply_markup)
    context.user_data["matches"] = matches
    return SELEZIONE

# Selezione finale
async def seleziona_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    selected_tag = query.data
    matches = context.user_data.get("matches", [])
    player = next((p for p in matches if p["attacker_tag"] == selected_tag), None)

    if not player:
        await query.edit_message_text("❌ Errore nella selezione.")
        return ConversationHandler.END

    return await salva_player(update, context, player)

# Salvataggio
async def salva_player(update: Update, context: ContextTypes.DEFAULT_TYPE, player):
    nome = player["attacker_name"]
    th = player["attacker_th"]
    tag = player["attacker_tag"]
    user_id = update.effective_user.id

    dati = carica_dati()
    lista = dati.get("lista_principale", [])

    if any(p["attacker_tag"] == tag for p in lista):
        await update.callback_query.message.reply_text(f"⚠️ Il player `{tag}` è già registrato.")
        return ConversationHandler.END

    lista.append({
        "nome_player": nome,
        "th": f"TH{th}",
        "attacker_tag": tag,
        "user_id": user_id
    })
    dati["lista_principale"] = lista
    salva_dati(dati)

    await update.callback_query.message.reply_text(
        f"✅ *Iscrizione completata!*\n\n"
        f"👤 *Nome:* {nome}\n🏰 *TH:* TH{th}\n🏷️ *Tag:* `{tag}`"
    )
    return ConversationHandler.END

# Annulla
async def annulla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iscrizione annullata ❌")
    return ConversationHandler.END

# Elimina interattiva
async def elimina_iscrizione_interattiva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dati = carica_dati()
    lista = dati.get("lista_principale", [])
    miei = [p for p in lista if p.get("user_id") == user_id]

    if not miei:
        await update.message.reply_text("❌ Non hai iscrizioni da cancellare.")
        return ConversationHandler.END

    keyboard = []
    row = []
    for p in miei:
        row.append(InlineKeyboardButton(p["nome_player"], callback_data=p["attacker_tag"]))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seleziona il nome da eliminare:", reply_markup=reply_markup)
    context.user_data["lista_completa"] = lista
    return ELIMINA_SCELTA

# Conferma eliminazione
async def conferma_eliminazione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    selected_tag = query.data
    user_id = update.effective_user.id
    lista = context.user_data.get("lista_completa", [])
    player = next((p for p in lista if p["attacker_tag"] == selected_tag), None)

    if not player:
        await query.edit_message_text("❌ Errore nella selezione.")
        return ConversationHandler.END

    if player["user_id"] != user_id:
        await query.edit_message_text("🚫 Non puoi eliminare questa iscrizione: non è tua.")
        return ConversationHandler.END

    nuova_lista = [p for p in lista if p["attacker_tag"] != selected_tag]
    salva_dati({"lista_principale": nuova_lista})

    await query.edit_message_text(
        f"🗑️ Iscrizione rimossa:\n👤 *{player['nome_player']}* | 🏰 {player['th']} | 🏷️ `{player['attacker_tag']}`"
    )
    return ConversationHandler.END
