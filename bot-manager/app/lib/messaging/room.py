from dataclasses import dataclass
from app.lib.messaging.room_history import RoomHistory
from app.lib.messaging.room_users import ChatRoomUsers


@dataclass
class ChatRoom:
    room_users: list[ChatRoomUsers]
    room_history: list[RoomHistory]
    name: str
    room_id: str
