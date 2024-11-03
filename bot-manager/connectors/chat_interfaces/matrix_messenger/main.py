from typing import Dict, List, Optional, Union

from nio import (
    AsyncClient,
    MatrixRoom,
    RoomGetStateError,
    RoomGetStateResponse,
    RoomMessageText,
)

from app.lib.bot_manager import BotManager
from app.lib.connector_base import ConnectorBase

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
    def __init__(self, bot: BotManager) -> None:
        self.bot: BotManager = bot
        self.client: AsyncClient = AsyncClient(matrix_homeserver, matrix_user)
        self.rooms: Dict[str, Dict[str, List[MessageContent] | RoomInfo]] = {}
        self.sent_messages: List[Dict[str, str | Optional[str]]] = (
            []
        )  # Track sent messages with room_id and content

    # Start the Matrix bot in a separate thread
    async def listen(self) -> None:

        await self.start_matrix_client()

    # Define the Matrix event handler for new messages
    async def room_message_callback(
        self, room: MatrixRoom, event: RoomMessageText
    ) -> None:
        sender: str = event.sender
        message: str = event.body
        room_id: str = room.room_id
        # Forward the message to the connector manager
        await self.bot.new_message_callback(room, event)

    # Initialize all rooms on startup
    async def init_rooms(self) -> None:
        joined_rooms = await self.client.joined_rooms()
        for room_id in joined_rooms.rooms:
            await self.init_room(room_id)

    async def init_room(self, room_id: str) -> None:
        # Initialize room details and load messages if necessary
        room_info: RoomInfo = await self.fetch_room_info(room_id)
        room_messages: List[MessageContent] = await self.fetch_room_messages(
            room_id
        )
        self.rooms[room_id] = {
            "info": room_info,
            "messages": room_messages,
        }

    async def fetch_room_info(self, room_id: str) -> RoomInfo:
        # Fetch room information such as room name and topic
        room = await self.client.room_get_state(room_id)
        room_info: RoomInfo = RoomInfo(name=room.room_id, room=room)
        return room_info

    async def fetch_room_messages(self, room_id: str) -> List[MessageContent]:
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

    # Send a message to the Matrix room through the Matrix client
    async def send_matrix_message(
        self, message_content: str, room_id: str, msg_type: str = "m.text"
    ) -> Optional[Dict[str, str]]:
        # Send message and store all data about the message and its status
        response = await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": msg_type,
                "body": message_content,
            },
        )
        message_info: Dict[str, str] = {
            "room_id": room_id,
            "content": message_content,
            "event_id": (
                response.event_id if response and response.event_id else ""
            ),
        }
        self.sent_messages.append(message_info)
        return message_info

    # Setup and run the Matrix client
    async def start_matrix_client(self) -> None:
        # Log into the Matrix client
        await self.client.login(matrix_password)

        # Initialize rooms and set up the event callback
        await self.init_rooms()

        # Register the new message callback to handle incoming messages
        self.client.add_event_callback(
            self.room_message_callback, RoomMessageText
        )

        # Start the sync loop to keep the client active and responsive
        await self.client.sync_forever(
            timeout=30000
        )  # Sync timeout in milliseconds

    # Placeholder method to illustrate room fetching with strict typing
    async def fetch_all_rooms(self) -> List[str]:
        # Fetch list of room IDs from the Matrix server
        return ["!roomid1:matrix.org", "!roomid2:matrix.org"]
