import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypedDict

from app.lib.logger import setup_logger


class Periods(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PeriodicSummaryDict(TypedDict):
    period: str
    period_start_date: int
    summary_text: str


@dataclass
class PeriodicSummary:
    period: Periods
    period_start_date: int
    summary_text: str

    @staticmethod
    def from_dict(data: PeriodicSummaryDict) -> "PeriodicSummary":
        return PeriodicSummary(
            period=Periods(data["period"]),
            period_start_date=data["period_start_date"],
            summary_text=data["summary_text"],
        )

    def to_dict(self) -> PeriodicSummaryDict:
        return {
            "period": self.period.value,
            "period_start_date": self.period_start_date,
            "summary_text": self.summary_text,
        }


class Roles(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ModelMessageDict(TypedDict):
    role: str
    content: str


@dataclass
class ModelMessage:
    role: Roles
    content: str

    @staticmethod
    def from_dict(data: ModelMessageDict) -> "ModelMessage":
        return ModelMessage(
            role=Roles(data["role"]),
            content=data["content"],
        )

    def to_dict(self) -> ModelMessageDict:
        return {
            "role": self.role.value,
            "content": self.content,
        }


class BotMemoryDict(TypedDict):
    periodic_summaries: dict[str, dict[int, PeriodicSummaryDict]]
    mind_map: str | None
    messages: dict[int, ModelMessageDict]


@dataclass
class BotMemory:
    periodic_summaries: dict[str, dict[int, PeriodicSummary]] = field(
        default_factory=dict
    )
    mind_map: Optional[str] = None
    messages: dict[int, ModelMessage] = field(default_factory=dict)

    def get_last_n_messages(self, n: int) -> list[ModelMessageDict]:
        # Step 1: Sort the timestamps in descending order
        sorted_timestamps_desc = sorted(self.messages.keys(), reverse=True)
        length: int = len(sorted_timestamps_desc)
        _n: int = length if length < n else n
        newest_timestamps = sorted_timestamps_desc[:_n]

        # from oldest to newest
        newest_timestamps_sorted = sorted(newest_timestamps)
        newest_messages_ordered = [
            self.messages[timestamp].to_dict()
            for timestamp in newest_timestamps_sorted
        ]
        return newest_messages_ordered

    @staticmethod
    def logger() -> logging.Logger:
        return setup_logger(
            "ConfigManager",
            logging.DEBUG,
        )

    def set_periodic_summary(
        self, interval: Periods, start_time: int, summary: str
    ) -> None:
        interval_summary = self.periodic_summaries.get(interval.value)
        if not interval_summary:
            self.periodic_summaries[interval.value] = {}
        self.periodic_summaries[interval.value][start_time] = PeriodicSummary(
            period=interval,
            period_start_date=start_time,
            summary_text=summary,
        )

    def get_periodic_summary(
        self, interval: Periods, start_time: int
    ) -> PeriodicSummary | None:
        return self.periodic_summaries.get(interval.value, {}).get(start_time)

    def add_message(self, role: Roles, content: str) -> None:
        self.messages[int(time.time())] = ModelMessage(role, content)

    @staticmethod
    def from_dict(data: BotMemoryDict) -> "BotMemory":
        periodic_summaries: dict[str, dict[int, PeriodicSummary]] = {}
        raw_summaries: dict[str, dict[int, PeriodicSummaryDict]] = data.get(
            "periodic_summaries", {}
        )
        for period, summaries in raw_summaries.items():
            periodic_summaries[period] = {
                date: PeriodicSummary.from_dict(summary)
                for date, summary in summaries.items()
            }

        messages: dict[int, ModelMessage] = {}
        raw_messages: dict[int, ModelMessageDict] = data.get("messages", {})
        for timestamp, message in raw_messages.items():
            messages[int(timestamp)] = ModelMessage.from_dict(message)
        return BotMemory(
            periodic_summaries=periodic_summaries,
            messages=messages,
            mind_map=data.get("mind_map", None),
        )

    def to_dict(self) -> BotMemoryDict:
        serialized_summaries = {
            period: {
                date: summary.to_dict() for date, summary in summaries.items()
            }
            for period, summaries in self.periodic_summaries.items()
        }
        serialized_messages = {
            int(timestamp): message.to_dict()
            for timestamp, message in self.messages.items()
        }
        return {
            "periodic_summaries": serialized_summaries,
            "mind_map": self.mind_map,
            "messages": serialized_messages,
        }
