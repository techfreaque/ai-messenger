import asyncio
import logging
import threading

from app.lib.connectors import ConnectorManager
from app.lib.logger import setup_logger
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.messaging.room import ChatRoom
from app.lib.messaging.room_users import ChatRoomUsers
from app.lib.messaging.rooms import ChatRooms
from app.lib.scheduler import WakeUpScheduler
from app.lib.storage.storage import Storage
from app.lib.web_server import WebServer
from profiles.default import Profile


class BotManager:
    def __init__(self):
        self.logger = setup_logger(
            "BotManager",
            logging.DEBUG,
        )
        self.threads: list[threading.Thread] = []
        self.data_lock = threading.Lock()
        self.should_dream: threading.Event = threading.Event()

        self.connector_manager: ConnectorManager = ConnectorManager(self)
        self.storage = Storage()
        self.profile: Profile = Profile()
        self.web_server: WebServer = WebServer(self)
        self.scheduler: WakeUpScheduler = WakeUpScheduler(self)

    def run_startup_tasks(self) -> None:
        """
        Start all loaded connectors by calling their 'listen' method.
        """
        for name, connector in self.connector_manager.connectors.items():
            if self.connector_manager.is_overridden(connector, "on_startup"):
                self.logger.info(f"Starting bot connector {name}...")

                def listener():
                    try:
                        asyncio.run(connector.on_startup())
                    except Exception as e:
                        self.logger.exception(
                            f"Bot connector {name} exited with an error: {e}"
                        )

                thread = threading.Thread(target=listener)
                thread.start()
                self.threads.append(thread)
                self.logger.info(f"Started bot connector {name}...")

    # def start_dreaming(self) -> None:
    #     self.should_dream.set()
    # for name, connector in self.connectors.items():
    #     if self.is_overridden(connector, "dream"):
    #         self.logger.info(f"Start dreaming on {name}...")

    #         def listener():
    #             try:
    #                 asyncio.run(connector.dream())
    #             except Exception as e:
    #                 self.logger.exception(f"Bot connector {name} exited with an error: {e}")

    #         thread = threading.Thread(target=listener)
    #         thread.start()
    #         self.threads.append(thread)
    #         self.logger.info(f"Started dreaming on {name}...")

    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ) -> SendChatMessageResponse:
        for connector in self.connector_manager.connectors.values():
            if self.connector_manager.is_overridden(connector, "send_message"):
                # currently only one send message connector allowed
                return await connector.send_message(
                    message=message, room_id=room_id, user_id=user_id
                )
        error = "Not able to send message, no connector with a send_message method found"
        self.logger.info(error)
        raise RuntimeError(error)

    async def get_rooms_list(self):
        room_list: ChatRooms = ChatRooms()
        for connector in self.connector_manager.connectors.values():
            if self.connector_manager.is_overridden(
                connector, "get_rooms_list"
            ):
                room_list.chat_rooms += (
                    await connector.get_rooms_list()
                ).chat_rooms
        return room_list

    async def get_room_history(
        self, room_id: str, start: int, to: int
    ) -> ChatRoom:
        for connector in self.connector_manager.connectors.values():
            if self.connector_manager.is_overridden(
                connector, "get_room_history"
            ):
                # currently only one get_room_history connector allowed
                return await connector.get_room_history(room_id, start, to)
        error = "Not able to get room history, no connector with a get_room_history method found"
        self.logger.info(error)
        raise RuntimeError(error)

    async def get_users(self, room_id: str) -> ChatRoomUsers:
        for connector in self.connector_manager.connectors.values():
            if self.connector_manager.is_overridden(connector, "get_users"):
                # currently only one get_users connector allowed
                return await connector.get_users(room_id)
        error = "Not able to get room history, no connector with a get_room_history method found"
        self.logger.info(error)
        raise RuntimeError(error)

    def execute_new_message_callback(
        self, room: ChatRoom, message: ReceiveChatMessage
    ) -> list[threading.Thread]:
        """
        can be triggered by other connectors e.g. matrix connector
        """
        threads: list[threading.Thread] = []
        for name, connector in self.connector_manager.connectors.items():
            if self.connector_manager.is_overridden(
                connector, "new_message_callback"
            ):
                self.logger.info(f"Starting bot connector {name}...")

                def listener():
                    try:
                        asyncio.run(
                            connector.new_message_callback(room, message)
                        )
                    except Exception as e:
                        self.logger.exception(
                            f"Bot connector {name} exited with an error: {e}"
                        )

                thread = threading.Thread(target=listener)
                thread.start()
                threads.append(thread)
                self.logger.info(f"Started bot connector {name}...")
        return threads
