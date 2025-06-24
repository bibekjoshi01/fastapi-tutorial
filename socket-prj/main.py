from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates

from chat import router as chat_router

app = FastAPI()

app.include_router(chat_router, tags=["chat"])

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.websocket("/ws/connect")
async def connection(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        print(f"Received data: {data}")
        await websocket.send_text(f"Message text was: {data}")


@app.get("/chat/{chat_id}", response_class=HTMLResponse)
async def chat_page(request: Request, chat_id: str):
    return templates.TemplateResponse("chat.html", {"request": request, "chat_id": chat_id})