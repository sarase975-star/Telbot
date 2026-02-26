import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===============================
# ENV VARIABLES
# ===============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_KEY = os.getenv("HF_API_KEY")
TOGETHER_KEY = os.getenv("TOGETHER_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")

# ===============================
# LLM CALL FUNCTIONS
# ===============================

async def call_huggingface(prompt: str) -> str:
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    payload = {"inputs": prompt}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)

    try:
        data = r.json()
    except Exception:
        return f"HuggingFace returned non-JSON:\n{r.text}"

    if isinstance(data, list):
        return data[0].get("generated_text", "No text returned from HuggingFace.")

    return str(data)


async def call_together(prompt: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)

    try:
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"Together API error:\n{r.text}"


async def call_cohere(prompt: str) -> str:
    url = "https://api.cohere.com/v2/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "command-r",
        "messages": [{"role": "user", "content": prompt}]
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)

    try:
        data = r.json()
        return data["message"]["content"][0]["text"]
    except Exception:
        return f"Cohere API error:\n{r.text}"


# ===============================
# SIMPLE ROUTER
# ===============================
def detect_agent(text: str) -> str:
    text = text.lower()
    if "french" in text or "learn" in text:
        return "french"
    if "business" in text or "startup" in text:
        return "business"
    return "general"


# ===============================
# TELEGRAM HANDLER
# ===============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    agent = detect_agent(user_text)

    try:
        if agent == "french":
            reply = await call_huggingface(user_text)
        elif agent == "business":
            reply = await call_together(user_text)
        else:
            reply = await call_cohere(user_text)
    except Exception as e:
        reply = f"Unexpected error:\n{str(e)}"

    await update.message.reply_text(reply[:4000])


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
