import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===============================
# ENV VARIABLES
# ===============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set")

# ===============================
# HUGGINGFACE ROUTER CLIENT
# ===============================

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# ===============================
# CALL HF MODEL
# ===============================

async def call_huggingface(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905:groq",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"HF Error:\n{str(e)}"

# ===============================
# TELEGRAM HANDLER
# ===============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    reply = await call_huggingface(user_text)

    await update.message.reply_text(reply[:4000])

# ===============================
# MAIN
# ===============================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
# ===============================
# MAIN
# ===============================
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
