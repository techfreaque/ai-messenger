from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_history import RoomHistory
from app.lib.messaging.room_users import ChatRoomUsers


class ChatRooms:
    def __init__(self) -> None:
        self.chat_rooms: list[ChatRoom] = []

    def add_room(
        self,
        room_users: list[ChatRoomUsers],
        room_history: list[RoomHistory],
        name: str,
        room_id: str,
    ) -> None:
        self.chat_rooms.append(
            ChatRoom(room_users, room_history, name, room_id)
        )

    def get_room_list(self) -> list[str]:
        return [room.get_base_info() for room in self.chat_rooms]
