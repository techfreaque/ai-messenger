from dataclasses import dataclass

from app.lib.messaging.room_user import ChatRoomUser


@dataclass
class ChatRoomUsers:
    room_users: list[ChatRoomUser]
