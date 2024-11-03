import asyncio
import logging
import threading
import time
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager

from app.lib.logger import setup_logger


class WakeUpScheduleType(Enum):
    timeout = "timeout"
    planned = "planned"


class WakeUpScheduler:
    def __init__(self, bot: "BotManager"):
        self.bot: "BotManager" = bot
        self.logger = setup_logger(
            "WakeUpScheduler",
            logging.DEBUG,
        )
        self.scheduled_wakeup: WakeUpSchedule = WakeUpSchedule(
            type=WakeUpScheduleType.timeout
        )

    def start_wakeup_scheduler(self) -> None:
        """
        Makes sure the bot wakes up according to the schedule
        """
        self.logger.info(f"Starting wakeup scheduler...")

        def _wakeup_schedule_main_loop():
            asyncio.run(self._wakeup_schedule_main_loop())

        thread = threading.Thread(target=_wakeup_schedule_main_loop)
        thread.start()
        self.bot.threads.append(thread)
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
                ) in self.bot.connector_manager.connectors.items():
                    if self.bot.connector_manager.is_overridden(
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
                    f"Scheduler running - next wakeup in {round((time.time() - self.scheduled_wakeup.wakeup_time)*-1 / 60 / 60, 1)} hours"
                )
                await asyncio.sleep(60)


class WakeUpSchedule:
    def __init__(
        self,
        sleep_time: int | None = None,
        type: WakeUpScheduleType = WakeUpScheduleType.planned,
    ) -> None:
        self.type: WakeUpScheduleType = type
        self.wakeup_time: int = int(
            time.time()
            + (sleep_time if sleep_time is not None else 24 * 60 * 60)
        )
