import asyncio
import logging
import threading
import time

from flask import Flask
from nio import MatrixRoom, RoomMessageText

from app.lib.connectors import ConnectorManager
from app.lib.logger import setup_logger
from app.lib.scheduler import WakeUpSchedule, WakeUpScheduleType
from app.lib.storage import Storage
from profiles.default import Profile


class BotManager:
    def __init__(self):
        self.logger = setup_logger(
            "BotManager",
            logging.DEBUG,
            max_bytes=2 * 1024 * 1024,
            backup_count=1,
        )
        self.connector_manager: ConnectorManager = ConnectorManager(self)

        self.should_dream: threading.Event = threading.Event()

        self.threads: list[threading.Thread] = []
        self.data_lock = threading.Lock()
        self.storage = Storage()
        self.app: Flask = Flask(__name__)
        self.profile: Profile = Profile()
        self.scheduled_wakeup: WakeUpSchedule = WakeUpSchedule(
            type=WakeUpScheduleType.timeout
        )

    def start_web_server(
        self,
    ) -> None:
        self.logger.info(
            f"Starting web server on port: {self.storage.bot_config.web_interface_port}"
        )
        self.app.run(
            host="0.0.0.0",
            port=self.storage.bot_config.web_interface_port,
            debug=False,
        )

    def start_all_bot_connectors(self) -> None:
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

    def watch_wakeup_schedule(self) -> None:
        """
        Makes sure the bot wakes up according to the schedule
        """
        self.logger.info(f"Starting wakeup scheduler...")

        def _wakeup_schedule_main_loop():
            asyncio.run(self._wakeup_schedule_main_loop())

        thread = threading.Thread(target=_wakeup_schedule_main_loop)
        thread.start()
        self.threads.append(thread)
        self.logger.info(f"Started wakeup_scheduler...")

    async def _wakeup_schedule_main_loop(self) -> None:
        while True:
            if (
                self.scheduled_wakeup
                and self.scheduled_wakeup.wakeup_time < time.time()
            ):
                for (
                    name,
                    connector,
                ) in self.connector_manager.connectors.items():
                    if self.connector_manager.is_overridden(
                        connector, "on_scheduled_wakeup"
                    ):
                        self.logger.info(
                            f"Executing scheduled wakeup on {name}..."
                        )
                        try:
                            await connector.on_scheduled_wakeup()
                        except Exception as e:
                            self.logger.exception(
                                f"Scheduled wakeup on {name} exited with an error: {e}"
                            )
                self.scheduled_wakeup = WakeUpSchedule(
                    type=WakeUpScheduleType.timeout
                )
            else:
                self.logger.info(
                    f"I'm sleeping - next wakeup in {round((time.time() - self.scheduled_wakeup.wakeup_time)*-1 / 60 / 60, 1)} hours"
                )
                await asyncio.sleep(60)

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

    async def new_message_callback(
        self, room: MatrixRoom, event: RoomMessageText
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
                        asyncio.run(connector.new_message_callback(room, event))
                    except Exception as e:
                        self.logger.exception(
                            f"Bot connector {name} exited with an error: {e}"
                        )

                thread = threading.Thread(target=listener)
                thread.start()
                threads.append(thread)
                self.logger.info(f"Started bot connector {name}...")
        return threads

    def init_web_server(self) -> None:
        """
        Initializes connectors with api's
        """
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        for name, connector in self.connector_manager.connectors.items():
            if self.connector_manager.is_overridden(connector, "api"):
                self.logger.info(f"Starting api connector {name}...")
                try:
                    connector.api()
                    self.logger.info(f"Started api connector {name}...")
                except Exception as e:
                    self.logger.exception(
                        f"Failed to start api on {name} connector, error: {e}"
                    )
