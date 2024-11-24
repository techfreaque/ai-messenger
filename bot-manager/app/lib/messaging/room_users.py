from app.lib.messaging.room_user import ChatRoomUser


class ChatRoomUsers:
    def __init__(self) -> None:
        self.room_users: list[ChatRoomUser] = []

    def add_member(self, id: str, name: str) -> None:
        self.room_users.append(ChatRoomUser(id, name))
