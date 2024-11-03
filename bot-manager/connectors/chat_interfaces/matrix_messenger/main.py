from typing import Dict, List, Optional, Union

from nio import (  # type: ignore
    AsyncClient,
    Event,
    MatrixRoom,
    RoomGetStateError,
    RoomGetStateResponse,
    RoomMessageText,
)

from app.lib.bot_manager import BotManager
from app.lib.connectors.connector_base import ConnectorBase
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import (
    SendChatMessageResponse,
    SendMessageType,
)
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms

# Matrix client settings
matrix_user: str = "freaque"
matrix_password: str = ".4-kC6FxwB:QVm3"
matrix_homeserver: str = (
    "https://matrix.org"  # Or your specific Matrix server URL
)

MessageContent = Dict[
    str, str
]  # Represents a single message with sender and content


class RoomInfo:
    name: str
    room: Union[RoomGetStateResponse, RoomGetStateError]

    def __init__(
        self, name: str, room: Union[RoomGetStateResponse, RoomGetStateError]
    ):
        self.name = name
        self.room = room


class Connector(ConnectorBase):
    def __init__(self, bot: BotManager, connector_name: str) -> None:
        super().__init__(bot, connector_name)
        self.client: AsyncClient = AsyncClient(matrix_homeserver, matrix_user)
        self.rooms: Dict[str, Dict[str, List[MessageContent] | RoomInfo]] = {}
        self.sent_messages: List[Dict[str, str | Optional[str]]] = []

    async def get_users(self, room_id: str) -> ChatRoomUsers:
        room: ChatRoom = await self.get_room_history(room_id)
        return ChatRoomUsers(room_users=room.get_users())

    async def on_startup(self) -> None:
        self.logger.info("Starting Matrix Client")
        await self.client.login(matrix_password)
        await self.get_rooms_list()

        self.client.add_event_callback(
            self._room_message_callback, RoomMessageText
        )

        # Start the sync loop to keep the client active and responsive
        await self.client.sync_forever(
            timeout=30000
        )  # Sync timeout in milliseconds
        self.logger.info("Started Matrix Client")

    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ) -> SendChatMessageResponse:
        # Send message and store all data about the message and its status
        response = await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": SendMessageType.TEXT.value,
                "body": message,
            },
        )
        return SendChatMessageResponse(
            success=response.status_code == 200, error=response.message
        )

    def _room_message_callback(self, room: MatrixRoom, event: Event) -> None:
        # sender: str = event.sender
        # message: str = event.body
        # room_id: str = room.room_id
        _room: ChatRoom = ChatRoom(
            name=room.display_name,
            room_id=room.room_id,
        )
        message: ReceiveChatMessage = ReceiveChatMessage(
            sender_id=event.sender_key or "TODOOO",
            sender_name=event.sender,
            message="TODO",
        )
        # Forward the message to the connector manager
        self.bot.execute_new_message_callback(_room, message)

    async def get_rooms_list(self) -> ChatRooms:
        joined_rooms = await self.client.joined_rooms()
        for room_id in joined_rooms.rooms:
            await self.init_room(room_id)
        return ChatRooms()

    async def get_room_history(
        self, room_id: str, start: int, to: int
    ) -> ChatRoom:
        # Initialize room details and load messages if necessary
        room_info: RoomInfo = await self._fetch_room_info(room_id)
        room_messages: List[MessageContent] = await self._fetch_room_messages(
            room_id
        )
        self.rooms[room_id] = {
            "info": room_info,
            "messages": room_messages,
        }
        return ChatRoom()

    async def _fetch_room_info(self, room_id: str) -> RoomInfo:
        # Fetch room information such as room name and topic
        room = await self.client.room_get_state(room_id)
        room_info: RoomInfo = RoomInfo(name=room.room_id, room=room)
        return room_info

    async def _fetch_room_messages(self, room_id: str) -> List[MessageContent]:
        # Fetch historical messages (last few messages for reference)
        messages: List[MessageContent] = []
        response = await self.client.room_messages(room_id, limit=10)
        if hasattr(response, "chunk"):
            for event in response.chunk:
                if isinstance(event, RoomMessageText):
                    messages.append(
                        {"sender": event.sender, "content": event.body}
                    )
        return messages
