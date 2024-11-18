from typing import Optional

from nio import (  # type: ignore
    AsyncClient,
    Event,
    JoinedMembersError,
    JoinedMembersResponse,
    JoinedRoomsError,
    JoinedRoomsResponse,
    MatrixRoom,
    ProfileGetDisplayNameError,
    ProfileGetDisplayNameResponse,
    ProfileSetDisplayNameError,
    ProfileSetDisplayNameResponse,
    RoomGetStateError,
    RoomGetStateResponse,
    RoomMember,
    RoomMessagesError,
    RoomMessagesResponse,
    RoomMessageText,
    RoomSendError,
    RoomSendResponse,
)

from app.lib.bot_manager import BotManager
from app.lib.messaging.bot_profile import SetUserNameResponse
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import (
    SendChatMessageResponse,
    SendMessageType,
)
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms
from app.lib.plugins.plugin_base import PluginBase

MessageContent = dict[
    str, str
]  # Represents a single message with sender and content


class Plugin(PluginBase):
    def __init__(self, bot: BotManager, plugin_name: str) -> None:
        super().__init__(bot, plugin_name)
        self.rooms: dict[
            str, dict[str, list[MessageContent] | RoomGetStateResponse]
        ] = {}
        self.sent_messages: list[dict[str, str | Optional[str]]] = []

    async def get_users(self, room_id: str) -> ChatRoomUsers:
        members: JoinedMembersResponse | JoinedMembersError = (
            await self.client.joined_members(room_id)
        )
        room_users: ChatRoomUsers = ChatRoomUsers()
        if isinstance(members, JoinedMembersResponse):
            raw_room_users: list[RoomMember] = members.members
            for member in raw_room_users:
                room_users.add_member(
                    id=member.user_id, name=member.display_name
                )

            return room_users
        self.logger.critical("Failed to get room users from matrix client")
        return room_users

    async def on_startup(self) -> None:
        self.logger.info("Starting Matrix Client")
        if (
            self.bot.storage.bot_config.matrix_user_name
            and self.bot.storage.bot_config.matrix_server
            and self.bot.storage.bot_config.matrix_user_password
        ):
            self.client: AsyncClient = AsyncClient(
                self.bot.storage.bot_config.matrix_server,
                self.bot.storage.bot_config.matrix_user_name,
            )
            await self.client.login(
                self.bot.storage.bot_config.matrix_user_password
            )
            await self.get_rooms_list()

            self.client.add_event_callback(
                self._room_message_callback, RoomMessageText
            )

            # Start the sync loop to keep the client active and responsive
            await self.client.sync_forever(
                # timeout=30000
            )
            self.logger.info("Started Matrix Client")
        else:
            self.logger.error(
                "Missing matrix user name, password and/or server"
            )

    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ) -> SendChatMessageResponse:
        # Send message and store all data about the message and its status
        response: RoomSendResponse | RoomSendError = (
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": SendMessageType.TEXT.value,
                    "body": message,
                },
            )
        )
        if isinstance(response, RoomSendResponse):
            return SendChatMessageResponse(success=True, error=None)
        return SendChatMessageResponse(success=False, error=response.message)

    def _room_message_callback(self, room: MatrixRoom, event: Event) -> None:
        # sender: str = event.sender
        # message: str = event.body
        # room_id: str = room.room_id
        message: ReceiveChatMessage = ReceiveChatMessage(
            sender_id=event.sender_key or "TODOOO",
            sender_name=event.sender,
            message="TODO",
            room_name=room.name or "TODOO",
            room_id=room.room_id,
        )
        # Forward the message to the plugin manager
        self.bot.execute_new_message_callback(message)

    async def get_rooms_list(self) -> ChatRooms:
        joined_rooms: JoinedRoomsResponse | JoinedRoomsError = (
            await self.client.joined_rooms()
        )
        if isinstance(joined_rooms, JoinedRoomsResponse):
            chat_rooms = ChatRooms()
            for room_id in joined_rooms.rooms:
                room_info = await self._fetch_room_info(room_id)
                if not room_info:
                    self.logger.critical(
                        f"get_rooms_list: Failed to get room info for {room_id}"
                    )

                chat_rooms.add_room(
                    room_users=[], room_history=[], name="TODO", room_id=room_id
                )
            return chat_rooms

        error_message = "Failed to get joined_rooms from matrix client"
        self.logger.critical(error_message)
        raise RuntimeError(error_message)

    async def get_room_history(
        self, room_id: str, start: int, to: int
    ) -> ChatRoom:
        # Initialize room details and load messages if necessary
        room_info = await self._fetch_room_info(room_id)
        if room_info:
            room_messages: list[MessageContent] | None = (
                await self._fetch_room_messages(room_id)
            )
            self.rooms[room_id] = {
                "info": room_info,
                "messages": room_messages,
            }
            return ChatRoom(
                room_users=room_users,
                room_history=room_history,
                name=name,
                room_id=room_id,
            )

    async def _fetch_room_info(
        self, room_id: str
    ) -> RoomGetStateResponse | None:
        self.client.set_displayname
        response: RoomGetStateResponse | RoomGetStateError = (
            await self.client.room_get_state(room_id)
        )
        if isinstance(response, RoomGetStateResponse):
            return response
        return None

    async def set_chat_user_name(self, new_name: str) -> SetUserNameResponse:
        change_response: (
            ProfileSetDisplayNameResponse | ProfileSetDisplayNameError
        ) = await self.client.set_displayname(
            f"{new_name} (bot)"  # dont lie plz
        )
        if isinstance(change_response, ProfileSetDisplayNameResponse):
            response: (
                ProfileGetDisplayNameResponse | ProfileGetDisplayNameError
            ) = await self.client.get_displayname()
            if isinstance(response, ProfileGetDisplayNameResponse):
                return SetUserNameResponse(name=new_name, error_message=None)
            return SetUserNameResponse(
                name=new_name, error_message=response.message
            )
        return SetUserNameResponse(
            name=new_name, error_message=change_response.message
        )

    async def _fetch_room_messages(
        self, room_id: str, limit: int
    ) -> list[MessageContent] | None:
        messages: list[MessageContent] = []
        response: RoomMessagesResponse | RoomMessagesError = (
            await self.client.room_messages(room_id, limit=limit)
        )
        if isinstance(response, RoomMessagesResponse):
            for event in response.chunk:
                if isinstance(event, RoomMessageText):
                    messages.append(
                        {"sender": event.sender, "content": event.body}
                    )
            return messages
        return None
