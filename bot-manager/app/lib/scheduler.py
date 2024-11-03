import time
from enum import Enum


class WakeUpScheduleType(Enum):
    timeout = "timeout"
    planned = "planned"


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
