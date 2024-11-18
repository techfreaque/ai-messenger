import asyncio
import logging
import threading

from app.lib.logger import setup_logger
from app.lib.messaging.bot_profile import SetUserNameResponse
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms
from app.lib.plugins import PluginManager
from app.lib.scheduler import Scheduler
from app.lib.storage.storage import Storage
from app.lib.webserver.webserver import WebServer
from profiles.default import Profile


class BotManager:
    def __init__(self):
        self.logger = setup_logger(
            "BotManager",
            logging.DEBUG,
        )
        self.threads: list[threading.Thread] = []
        self.data_lock = threading.Lock()

        self.plugin_manager: PluginManager = PluginManager(self)
        self.storage = Storage()
        self.profile: Profile = Profile()
        self.web_server: WebServer = WebServer(self)
        self.scheduler: Scheduler = Scheduler(self)

    def run_startup_tasks(self) -> None:
        """
        Start all loaded plugins by calling their 'listen' method.
        """
        for name, plugin in self.plugin_manager.plugins.items():
            if self.plugin_manager.is_overridden(plugin, "on_startup"):
                self.logger.info(f"Starting bot plugin {name}...")

                # def _on_startup():
                try:
                    asyncio.run(plugin.on_startup())
                except Exception as e:
                    self.logger.exception(
                        f"Bot plugin {name} exited with an error: {e}"
                    )

                # thread = threading.Thread(target=_on_startup)
                # thread.start()
                # self.threads.append(thread)
                self.logger.info(f"Started bot plugin {name}...")

    async def set_chat_user_name(self, new_name: str) -> SetUserNameResponse:
        for plugin in self.plugin_manager.plugins.values():
            if self.plugin_manager.is_overridden(plugin, "set_chat_user_name"):
                # currently only one send message plugin allowed
                return await plugin.set_chat_user_name(new_name=new_name)
        error = "Not able to send message, no plugin with a send_message method found"
        self.logger.info(error)
        raise RuntimeError(error)

    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ) -> SendChatMessageResponse:
        for plugin in self.plugin_manager.plugins.values():
            if self.plugin_manager.is_overridden(plugin, "send_message"):
                # currently only one send message plugin allowed
                return await plugin.send_message(
                    message=message, room_id=room_id, user_id=user_id
                )
        error = "Not able to send message, no plugin with a send_message method found"
        self.logger.info(error)
        raise RuntimeError(error)

    async def get_rooms_list(self):
        room_list: ChatRooms = ChatRooms()
        for plugin in self.plugin_manager.plugins.values():
            if self.plugin_manager.is_overridden(plugin, "get_rooms_list"):
                room_list.chat_rooms += (
                    await plugin.get_rooms_list()
                ).chat_rooms
        return room_list

    async def get_room_history(
        self, room_id: str, start: int, to: int
    ) -> ChatRoom:
        for plugin in self.plugin_manager.plugins.values():
            if self.plugin_manager.is_overridden(plugin, "get_room_history"):
                # currently only one get_room_history plugin allowed
                return await plugin.get_room_history(room_id, start, to)
        error = "Not able to get room history, no plugin with a get_room_history method found"
        self.logger.info(error)
        raise RuntimeError(error)

    async def get_users(self, room_id: str) -> ChatRoomUsers:
        for plugin in self.plugin_manager.plugins.values():
            if self.plugin_manager.is_overridden(plugin, "get_users"):
                # currently only one get_users plugin allowed
                return await plugin.get_users(room_id)
        error = "Not able to get room history, no plugin with a get_room_history method found"
        self.logger.info(error)
        raise RuntimeError(error)

    def execute_new_message_callback(
        self, message: ReceiveChatMessage
    ) -> list[threading.Thread]:
        """
        can be triggered by other plugins e.g. matrix plugin
        """
        threads: list[threading.Thread] = []
        for name, plugin in self.plugin_manager.plugins.items():
            if self.plugin_manager.is_overridden(
                plugin, "new_message_callback"
            ):
                self.logger.info(f"Starting bot plugin {name}...")

                def listener():
                    try:
                        asyncio.run(plugin.new_message_callback(message))
                    except Exception as e:
                        self.logger.exception(
                            f"Bot plugin {name} exited with an error: {e}"
                        )

                thread = threading.Thread(target=listener)
                thread.start()
                threads.append(thread)
                self.logger.info(f"Started bot plugin {name}...")
        return threads
