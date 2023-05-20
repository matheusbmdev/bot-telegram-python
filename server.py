from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv() 

app = FastAPI()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

@app.post("/conversation")
async def conversation(req: Request):
    body = await req.json()
    message = body["message"]
    chat_id = body["chat_id"]  # Obter o chat_id do corpo da requisição
    # Aqui você pode implementar a lógica para gerar uma resposta
    response = f"Você disse: {message}"
    await send_tg_message(response, chat_id)  # Adicione o chat_id como argumento

async def send_tg_message(message: str, chat_id: str):  # Adicione chat_id como argumento
    tg_msg = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(API_URL, json=tg_msg)

