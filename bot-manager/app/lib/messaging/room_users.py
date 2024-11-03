from app.lib.messaging.room_user import ChatRoomUser


class ChatRoomUsers:
    def __init__(self):
        self.room_users: list[ChatRoomUser] = []

    def add_member(self, id: str, name: str):
        self.room_users.append(ChatRoomUser(id, name))
