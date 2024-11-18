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


class Scheduler:
    def __init__(self, bot: "BotManager"):
        self.bot: "BotManager" = bot
        self.logger = setup_logger(
            "Scheduler",
            logging.DEBUG,
        )
        self.scheduled_wakeup: WakeUpSchedule = WakeUpSchedule(
            type=WakeUpScheduleType.planned, sleep_time=0  # start right away
        )
        self.should_dream: threading.Event = threading.Event()

    def start_scheduler(self) -> None:
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
            if self.scheduled_wakeup.wakeup_time < time.time():
                for (
                    name,
                    plugin,
                ) in self.bot.plugin_manager.plugins.items():
                    if self.bot.plugin_manager.is_overridden(
                        plugin, "on_scheduled_wakeup"
                    ):
                        self.logger.info(
                            f"Executing scheduled wakeup on {name}..."
                        )
                        try:
                            await plugin.on_scheduled_wakeup()
                        except Exception as e:
                            self.logger.exception(
                                f"Scheduled wakeup on {name} exited with an error: {e}"
                            )
                self.scheduled_wakeup = WakeUpSchedule(
                    type=WakeUpScheduleType.timeout
                )
            else:
                if self.should_dream.is_set():
                    self.logger.info(
                        f"Still dreaming - next wakeup in {round((time.time() - self.scheduled_wakeup.wakeup_time)*-1 / 60 / 60, 1)} hours"
                    )
                    await asyncio.sleep(60)
                else:
                    self.logger.info(
                        f"Starting dreaming - next wakeup in {round((time.time() - self.scheduled_wakeup.wakeup_time)*-1 / 60 / 60, 1)} hours"
                    )
                    self.should_dream.set()
                    self.start_dreaming()

    def start_dreaming(self) -> None:
        self.should_dream.set()
        for name, plugin in self.bot.plugin_manager.plugins.items():
            if self.bot.plugin_manager.is_overridden(plugin, "dream"):
                self.logger.info(f"Start dreaming on {name}...")

                def dream():
                    try:
                        asyncio.run(plugin.dream())
                    except Exception as e:
                        self.logger.exception(
                            f"Bot plugin {name} exited dreaming with an error: {e}"
                        )

                thread = threading.Thread(target=dream)
                thread.start()
                self.bot.threads.append(thread)
                self.logger.info(f"Started dreaming on {name}...")


class WakeUpSchedule:
    def __init__(
        self,
        sleep_time: int | None = None,
        type: WakeUpScheduleType = WakeUpScheduleType.planned,
    ) -> None:
        default_sleep_time = 24 * 60 * 60
        self.type: WakeUpScheduleType = type
        self.wakeup_time: int = int(
            time.time()
            + (sleep_time if sleep_time is not None else default_sleep_time)
        )
        self.sleep_time: int = (
            default_sleep_time if sleep_time is None else sleep_time
        )
