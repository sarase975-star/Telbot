import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Load API keys from environment
HF_KEY = os.environ.get("HF_API_KEY")
TOGETHER_KEY = os.environ.get("TOGETHER_API_KEY")
COHERE_KEY = os.environ.get("COHERE_API_KEY")

# ---- Functions to call free LLMs ----

async def call_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    data = {"inputs": prompt}
    try:
        r = requests.post("https://api-inference.huggingface.co/models/mistral-7b", headers=headers, json=data)
        r.raise_for_status()
        return r.json()[0]["generated_text"]
    except Exception as e:
        return f"HuggingFace error: {e}"

async def call_together(prompt):
    headers = {"Authorization": f"Bearer {TOGETHER_KEY}"}
    data = {"input": prompt}
    try:
        r = requests.post("https://api.together.xyz/inference/gpt", headers=headers, json=data)
        r.raise_for_status()
        return r.json().get("output", "Together AI did not respond.")
    except Exception as e:
        return f"Together AI error: {e}"

async def call_cohere(prompt):
    headers = {"Authorization": f"Bearer {COHERE_KEY}"}
    data = {"prompt": prompt, "max_tokens": 100}
    try:
        r = requests.post("https://api.cohere.com/v1/generate", headers=headers, json=data)
        r.raise_for_status()
        return r.json()["generations"][0]["text"]
    except Exception as e:
        return f"Cohere error: {e}"

# ---- Telegram message handler ----

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # Simple intent detection
    if "french" in text:
        reply = await call_huggingface(text)
    elif "business" in text:
        reply = await call_together(text)
    else:
        reply = await call_cohere(text)

    await update.message.reply_text(reply)

# ---- Main bot setup ----

def main():
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
