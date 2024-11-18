import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from app.lib.logger import setup_logger
from app.lib.messaging.bot_profile import SetUserNameResponse
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class PluginBase:
    """
    Protocol for plugin classes. All plugins must implement this class
    """

    bot: "BotManager"
    logger: logging.Logger

    def __init__(self, bot: "BotManager", plugin_name: str):
        self.bot: "BotManager" = bot
        self.logger: logging.Logger = setup_logger(
            "Plugin " + plugin_name,
            logging.DEBUG,
        )

    ##
    ## callbacks
    ##
    @abstractmethod
    async def dream(self) -> None:
        """
        while there is nothing to do you can reorganize data when, start training or just nothing
        """

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
    async def new_message_callback(self, message: ReceiveChatMessage) -> None:
        """
        This gets called when a new message comes in from a messaging plugin
        """

    ##
    ## web api plugins
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
    async def set_chat_user_name(self, new_name: str) -> SetUserNameResponse:
        """
        Gets called when the model wants to set/change its user name
        """

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
