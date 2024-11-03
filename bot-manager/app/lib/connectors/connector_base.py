import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from app.lib.logger import setup_logger
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class ConnectorBase:
    """
    Protocol for connector classes. All connectors must implement this class
    """

    bot: "BotManager"
    logger: logging.Logger

    def __init__(self, bot: "BotManager", connector_name: str):
        self.bot: "BotManager" = bot
        self.logger: logging.Logger = setup_logger(
            "Connector " + connector_name,
            logging.DEBUG,
        )

    ##
    ## callbacks
    ##
    @abstractmethod
    async def on_startup(
        self,
    ) -> None:
        """
        This gets called on startup
        """

    @abstractmethod
    async def on_scheduled_wakeup(
        self,
    ) -> None:
        """
        This gets called when the sleep timeout is reached or if a wakeup was scheduled
        """

    @abstractmethod
    async def new_message_callback(
        self, room: ChatRoom, message: ReceiveChatMessage
    ) -> None:
        """
        This gets called when a new message comes in from a messaging connector
        """

    ##
    ## web api connectors
    ##
    @abstractmethod
    def api(
        self,
    ) -> None:
        """
        Add your web apis here
        """

    ##
    ## functions that the model can directly trigger
    ##
    @abstractmethod
    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ) -> SendChatMessageResponse:
        """
        Gets called when the model want to send_message
        """

    @abstractmethod
    async def get_rooms_list(self) -> ChatRooms:
        """
        Gets called when the model want to get_rooms_list
        """

    @abstractmethod
    async def get_room_history(
        self, room_id: str, start: int, to: int
    ) -> ChatRoom:
        """
        Gets called when the model want to get_room_history
        """

    @abstractmethod
    async def get_users(self, room_id: str) -> ChatRoomUsers:
        """
        Gets called when the model want to get_users
        """
