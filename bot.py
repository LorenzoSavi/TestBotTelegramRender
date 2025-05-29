import logging
import os
import random
import threading # Per eseguire Flask in un thread separato
from flask import Flask # Importa Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configurazione Flask ---
# Render di solito imposta la variabile PORT
# Se non la trova, usa 8080 di default (ma Render dovrebbe gestirla)
FLASK_PORT = int(os.environ.get('PORT', 8080))
app = Flask(__name__)

@app.route('/')
def health_check():
    """Endpoint per l'health check di Render."""
    return "Bot is running!", 200
# --- Fine Configurazione Flask ---

# Abilita il logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variabile d'ambiente per il token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN non trovato nelle variabili d'ambiente!")
    # In un ambiente server, potresti voler sollevare un'eccezione o uscire in modo più pulito
    # ma per semplicità, usiamo exit()
    exit()

# Simboli per la slot machine
SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍉", "🍇", "🔔", "💎", "7️⃣"]

# Funzione per il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Ciao {user.mention_html()}!",
    )
    await update.message.reply_text(
        "Questo è il secondo messaggio di test dal bot!\nScrivi 888 per provare la slot machine!"
    )

# Funzione per la slot machine
async def slot_machine_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Utente {update.effective_user.username} ha attivato la slot machine.")
    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    result_text = f"🎰 **Slot Machine** 🎰\n\n   {reels[0]} | {reels[1]} | {reels[2]}   \n\n"
    if reels[0] == reels[1] == reels[2]:
        result_text += "🎉 **JACKPOT!!!** 🎉\nComplimenti, hai vinto alla grande!"
    elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        result_text += "💰 **Piccola vincita!** 💰\nNon male, due simboli uguali!"
    else:
        result_text += "☠️ **Peccato!** ☠️\nNessuna combinazione vincente. Riprova!"
    await update.message.reply_text(result_text, parse_mode="Markdown")

def run_flask_app():
    """Avvia l'app Flask."""
    # Usa '0.0.0.0' per rendere il server accessibile esternamente (necessario per Render)
    app.run(host='0.0.0.0', port=FLASK_PORT)

def main() -> None:
    """Avvia il bot e il server Flask."""
    # Crea l'Application e passagli il token del tuo bot.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^888$"), slot_machine_handler))

    # Avvia Flask in un thread separato
    # Questo permette a Flask di gestire le richieste HTTP mentre il bot fa polling.
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True # Permette al programma principale di uscire anche se il thread è in esecuzione
    flask_thread.start()
    logger.info(f"Server Flask in ascolto sulla porta {FLASK_PORT} in un thread separato.")

    # Avvia il Bot (polling)
    logger.info("Bot Telegram in avvio (polling)...")
    application.run_polling()

if __name__ == "__main__":
    main()