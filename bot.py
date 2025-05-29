import logging
import os
import random # Importa il modulo random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes # Aggiungi MessageHandler e filters

# Abilita il logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variabile d'ambiente per il token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN non trovato nelle variabili d'ambiente!")
    exit()

# Simboli per la slot machine
SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍉", "🍇", "🔔", "💎", "7️⃣"]

# Funzione per il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Invia due messaggi quando viene invocato il comando /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Ciao {user.mention_html()}!",
    )
    await update.message.reply_text(
        "Questo è il secondo messaggio di test dal bot!\nScrivi 888 per provare la slot machine!"
    )

# Funzione per la slot machine
async def slot_machine_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simula una slot machine quando l'utente digita '888'."""
    logger.info(f"Utente {update.effective_user.username} ha attivato la slot machine.")
    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    
    result_text = f"🎰 **Slot Machine** 🎰\n\n   {reels[0]} | {reels[1]} | {reels[2]}   \n\n"

    # Controlla se c'è una vincita
    if reels[0] == reels[1] == reels[2]:
        result_text += "🎉 **JACKPOT!!!** 🎉\nComplimenti, hai vinto alla grande!"
    elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        result_text += "💰 **Piccola vincita!** 💰\nNon male, due simboli uguali!"
    else:
        result_text += "☠️ **Peccato!** ☠️\nNessuna combinazione vincente. Riprova!"
        
    await update.message.reply_text(result_text, parse_mode="Markdown")


def main() -> None:
    """Avvia il bot."""
    # Crea l'Application e passagli il token del tuo bot.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Gestore per il comando /start
    application.add_handler(CommandHandler("start", start))

    # Gestore per il messaggio "888" (slot machine)
    # Usa filters.Regex("^888$") per assicurarsi che il messaggio sia esattamente "888"
    application.add_handler(MessageHandler(filters.Regex("^888$"), slot_machine_handler))

    # Avvia il Bot (polling)
    logger.info("Bot in avvio...")
    application.run_polling()

if __name__ == "__main__":
    main()