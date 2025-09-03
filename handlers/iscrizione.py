import asyncio
import requests
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from utils.file_utils import carica_dati, salva_dati
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

NOME, SELEZIONE, ELIMINA_SCELTA = range(3)

# Inizio iscrizione
async def start_iscrizione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "📌 Inserisci il nome del player da iscrivere:",
        reply_markup=ForceReply()
    )
    return NOME


# Ricezione nome e ricerca
async def ricevi_nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Per favore rispondi al messaggio con la domanda usando il campo sotto.")
        return NOME

    nome_inserito = update.message.text.strip().lower()
    print("📥 Nome inserito:", repr(nome_inserito))

    # 🔄 Recupero dati da API esterna
    try:
        response = requests.get("https://api.warmachine.cc/v1/playerlist")
        response.raise_for_status()
        player_list = response.json()
        print("📂 Dati ricevuti:", len(player_list), "players")
    except Exception as e:
        print("❌ Errore API:", e)
        await update.message.reply_text("❌ Errore nel recupero dei dati esterni.")
        return ConversationHandler.END

    # 🔍 Cerca match
    matches = [
        p for p in player_list
        if p.get("attacker_name") and nome_inserito in p["attacker_name"].strip().lower()
    ]
    print("🔍 Match trovati:", len(matches))
    for m in matches:
        print(" →", m["attacker_name"], "|", m["attacker_tag"])

    if not matches:
        await update.message.reply_text("⚠️ Nessun player trovato con quel nome. Riprova.")
        return NOME

    if len(matches) == 1:
        return await salva_player(update, context, matches[0])

    # 🔘 Selezione interattiva
    keyboard = [
        [InlineKeyboardButton(p["attacker_name"], callback_data=p["attacker_tag"])]
        for p in matches
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["matches"] = matches
    print("💾 Match salvati in context.user_data")

    await update.message.reply_text("🔍 Seleziona il player giusto:", reply_markup=reply_markup)
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
    lega = player.get("last_cwl_league", "Non assegnata")

    dati = carica_dati()
    lista = dati.get("lista_principale", [])

    # Verifica se il player è già registrato
    if any(p["attacker_tag"] == tag for p in lista):
        messaggio = f"⚠️ Il player `{tag}` è già registrato."
        messaggio = escape_markdown(messaggio, version=2)
        if update.callback_query:
            await update.callback_query.message.reply_text(messaggio, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(messaggio, parse_mode="MarkdownV2")
        return ConversationHandler.END

    # Aggiungi il player alla lista
    lista.append({
        "nome_player": nome,
        "th": f"TH{th}",
        "attacker_tag": tag,
        "user_id": user_id,
        "last_cwl_league": lega
    })
    dati["lista_principale"] = lista
    salva_dati(dati)

    # Messaggio di conferma
    testo = (
        f"✅ Iscrizione completata!\n\n"
        f"👤 Nome: {nome}\n"
        f"🏰 TH: TH{th}\n"
        f"🏷️ Tag: `{tag}`\n"
        f"🏆 Lega CWL: {lega}\n\n"
        "📌 Il player è stato aggiunto alla lista CWL."
    )
    testo = escape_markdown(testo, version=2)

    if update.callback_query:
        await update.callback_query.message.reply_text(testo, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(testo, parse_mode="MarkdownV2")

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
