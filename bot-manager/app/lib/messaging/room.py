from dataclasses import dataclass

from app.lib.messaging.room_history import RoomHistory
from app.lib.messaging.room_users import ChatRoomUsers


@dataclass
class ChatRoom:
    room_users: list[ChatRoomUsers]
    room_history: list[RoomHistory]
    name: str
    room_id: str

    def get_base_info(self) -> str:
        return f"name: {self.name}- room_id: {self.room_id} - room_users length: {len(self.room_users)} - room_history length: {len(self.room_history)}"
