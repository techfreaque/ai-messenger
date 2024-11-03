from dataclasses import dataclass
from app.lib.messaging.room import ChatRoom


@dataclass
class ChatRooms:
    chat_rooms: list[ChatRoom]
