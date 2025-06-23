from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.websocket("/ws/connect")
async def connection(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        print(f"Received data: {data}")
        await websocket.send_text(f"Message text was: {data}")

chat_rooms = {}


@app.websocket("/ws/chat/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: str):
    await websocket.accept()

    if chat_id not in chat_rooms:
        chat_rooms[chat_id] = []

    chat_rooms[chat_id].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received: {message} from room: {chat_id}")

            for client in chat_rooms[chat_id]:
                if client != websocket:
                    await client.send_text(message)

    except WebSocketDisconnect:
        chat_rooms[chat_id].remove(websocket)
        if not chat_rooms[chat_id]:
            del chat_rooms[chat_id]
        print(f"WebSocket disconnected from chat room {chat_id}")


@app.get("/chat/{chat_id}")
async def chat_page(chat_id: str):
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
        <body>
          <h2>Simple Chat: {chat_id}</h2>
          <input id="msg" placeholder="Type a message" />
          <button onclick="send()">Send</button>
          <ul id="messages"></ul>

          <script>
            const chatId = "{chat_id}";
            const ws = new WebSocket("ws://localhost:8000/ws/chat/" + chatId);

            ws.onmessage = (event) => {{
              const li = document.createElement("li");
              li.innerText = event.data;
              console.log("Received message:", event.data);
              document.getElementById("messages").appendChild(li);
            }};

            function send() {{
              const input = document.getElementById("msg");
              if (input.value.trim() !== "") {{
                ws.send(input.value);
                input.value = "";
              }}
            }}
          </script>
        </body>
        </html>
        """
    )
