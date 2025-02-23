from datetime import datetime
from typing import List, Dict
import pytz
from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from chats_database.models import ChatSession
from common.chatting_common import get_chats
from constants.constants import RoleEntities
from data.model.chat_message_data_model import ChatMessage
from gpt.conversation import conversation
from utils.parse_null import pars_null

router = APIRouter(prefix="/chat", tags=["Chatting"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(str(message))


manager = ConnectionManager()


class CurrentUser(BaseModel):
    user_id: str
    username: str


async def get_current_user() -> CurrentUser:
    return CurrentUser(user_id="123456", username="test_user")


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        session_id: str | None = None,
        current_user: CurrentUser = Depends(get_current_user)
):
    session_id = pars_null(session_id)
    print(session_id)

    session = await ChatSession.get(session_id)
    if not session:
        session = ChatSession(user_id=current_user.user_id, title="Chat Session")
        await ChatSession.insert(session)
        session_id = str(session.id)

    await manager.connect(session_id, websocket)

    try:
        while True:
            user_message = await websocket.receive_text()

            new_user_message = ChatMessage(role=RoleEntities.user.name, content=user_message)
            session.messages.append(new_user_message)

            response = conversation(get_chats(session.messages))

            new_assistant_message = ChatMessage(role=RoleEntities.assistant.name, content=response)
            session.messages.append(new_assistant_message)

            session.updated_at = datetime.now(pytz.UTC)

            await ChatSession.save(session)

            await manager.broadcast(session_id, response)
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
        await manager.broadcast(session_id, {"info": "One client disconnected."})
