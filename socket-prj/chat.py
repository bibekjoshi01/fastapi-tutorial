from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json

from utils import generate_random_name

router = APIRouter()

chat_rooms = {}


@router.websocket("/ws/chat/{chat_id}")
async def chat(websocket: WebSocket, chat_id: str):
    await websocket.accept()

    if chat_id not in chat_rooms:
        chat_rooms[chat_id] = []

    existing_names = {user['username'] for user in chat_rooms[chat_id]}
    while True:
        username = generate_random_name()
        if username not in existing_names:
            break

    chat_rooms[chat_id].append({'socket': websocket, 'username': username})

    join_msg = json.dumps({"sender": "System", "message": f"{username} joined the chat."})
    for client in chat_rooms[chat_id]:
        await client['socket'].send_text(join_msg)

    try:
        while True:
            message_text = await websocket.receive_text()

            message = json.dumps({
                "sender": username,
                "message": message_text
            })

            for client in chat_rooms[chat_id]:
                await client['socket'].send_text(message)

    except WebSocketDisconnect:
        # Remove disconnected user
        chat_rooms[chat_id] = [
            client for client in chat_rooms[chat_id] if client["socket"] != websocket
        ]
        if not chat_rooms[chat_id]:
            del chat_rooms[chat_id]
        else:
            leave_msg = json.dumps({"sender": "System", "message": f"{username} left the chat."})
            for client in chat_rooms[chat_id]:
                await client["socket"].send_text(leave_msg)

        print(f"{username} disconnected from chat {chat_id}")

