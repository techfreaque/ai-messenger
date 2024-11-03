from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from logging import Logger
from pathlib import Path
from typing import Optional, TypedDict

from app.lib.logger import setup_logger


class Periods(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    UNDEFINED = "undefined"


class PeriodicSummaryDict(TypedDict):
    period: str
    period_start_date: str
    summary_text: str


@dataclass
class PeriodicSummary:
    period: Periods
    period_start_date: str  # TODO parse format D-M-Y
    summary_text: str

    @staticmethod
    def from_dict(data: PeriodicSummaryDict) -> PeriodicSummary:
        return PeriodicSummary(
            period=Periods(data.get("period", Periods.UNDEFINED.value)),
            period_start_date=data.get(
                "period_start_date", Periods.UNDEFINED.value
            ),
            summary_text=data.get("summary_text", Periods.UNDEFINED.value),
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
    UNDEFINED = "undefined"


class ModelMessageDict(TypedDict):
    role: str
    content: str


@dataclass
class ModelMessage:
    role: Roles
    content: str

    @staticmethod
    def from_dict(data: ModelMessageDict) -> ModelMessage:
        return ModelMessage(
            role=Roles(data.get("role", "undefined")),
            content=data.get("content", "undefined"),
        )

    def to_dict(self) -> ModelMessageDict:
        return {
            "role": self.role.value,
            "content": self.content,
        }


class BotMemoryDict(TypedDict):
    periodic_summaries: dict[str, dict[str, PeriodicSummaryDict]]
    mind_map: str | None
    messages: dict[int, ModelMessageDict]


@dataclass
class BotMemory:
    periodic_summaries: dict[str, dict[str, PeriodicSummary]] = field(
        default_factory=dict
    )
    mind_map: Optional[str] = None
    messages: dict[int, ModelMessage] = field(default_factory=dict)

    def set_periodic_summary(
        self, interval: str, start_time: str, summary: str
    ):
        interval_summary = self.periodic_summaries.get(interval)
        if not interval_summary:
            self.periodic_summaries[interval] = {}
        self.periodic_summaries[interval][start_time] = PeriodicSummary(
            period=Periods(interval),
            period_start_date=start_time,
            summary_text=summary,
        )

    def get_periodic_summary(
        self, interval: str, start_time: str
    ) -> PeriodicSummary | None:
        return self.periodic_summaries.get(interval, {}).get(start_time)

    def add_message(self, role: Roles, content: str):
        self.messages[int(time.time())] = ModelMessage(role, content)

    @staticmethod
    def from_dict(data: BotMemoryDict) -> BotMemory:
        periodic_summaries: dict[str, dict[str, PeriodicSummary]] = {}
        raw_summaries: dict[str, dict[str, PeriodicSummaryDict]] = data.get(
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
            messages[timestamp] = ModelMessage.from_dict(message)
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
            timestamp: message.to_dict()
            for timestamp, message in self.messages.items()
        }
        return {
            "periodic_summaries": serialized_summaries,
            "mind_map": self.mind_map,
            "messages": serialized_messages,
        }


class ConfigDict(TypedDict):
    id: str
    profile_name: str
    bot: BotConfigDict
    web_interface: WebInterfaceConfigDict
    message_interface: MessageInterfaceConfigDict


class WebInterfaceConfigDict(TypedDict):
    web_interface_port: int
    web_interface_api_key: str


class BotConfigDict(TypedDict):
    bot_name: Optional[str]
    bot_timeout: int
    model_name: str
    model_api_key: Optional[str]
    model_api_url: str


class MessageInterfaceConfigDict(TypedDict):
    matrix_user_name: Optional[str]
    matrix_user_password: Optional[str]
    matrix_server: str


@dataclass
class Config:
    id: str  # Changed from Optional[str] to str
    bot_name: Optional[str]
    bot_profile_name: str  # Changed from Optional[str] to str
    bot_timeout: int
    model_api_key: Optional[str]
    model_api_url: str
    model_name: str
    web_interface_port: int
    web_interface_api_key: str
    matrix_user_name: Optional[str]
    matrix_user_password: Optional[str]
    matrix_server: str

    @classmethod
    def from_default(cls) -> "Config":
        return cls.from_dict(cls.get_default_config())

    @staticmethod
    def get_default_config() -> ConfigDict:
        bot: BotConfigDict = {
            "bot_name": None,
            "bot_timeout": 86400,  # one day
            "model_name": "gpt-4o-mini",
            "model_api_key": None,
            "model_api_url": "https://api.openai.com/v1/chat/completions",
        }
        web_interface: WebInterfaceConfigDict = {
            "web_interface_port": 5000,
            "web_interface_api_key": str(uuid.uuid4()),
        }
        message_interface: MessageInterfaceConfigDict = {
            "matrix_user_name": None,
            "matrix_user_password": None,
            "matrix_server": "matrix.org",
        }
        config: ConfigDict = {
            "id": str(uuid.uuid4()),
            "profile_name": "anon bot",
            "bot": bot,
            "web_interface": web_interface,
            "message_interface": message_interface,
        }
        return config

    @classmethod
    def from_dict(cls, data: ConfigDict) -> "Config":
        default_config = cls.get_default_config()

        def get_value(
            restored_data: dict[str, str | dict[str, str]],
            default_data: dict[str, str | dict[str, str]],
            _key: str,
        ):
            return restored_data.get(_key, default_data.get(_key, "error"))

        bot_config: BotConfigDict = get_value(data, default_config, "bot")  # type: ignore
        web_interface_config: WebInterfaceConfigDict = get_value(data, default_config, "web_interface")  # type: ignore
        message_interface_config: MessageInterfaceConfigDict = get_value(data, default_config, "message_interface")  # type: ignore
        return Config(
            id=get_value(data, default_config, "id"),  # type: ignore
            bot_profile_name=get_value(data, default_config, "profile_name"),  # type: ignore
            bot_name=get_value(bot_config, default_config["bot"], "bot_name"),  # type: ignore
            bot_timeout=get_value(bot_config, default_config["bot"], "bot_timeout"),  # type: ignore
            model_name=get_value(bot_config, default_config["bot"], "model_name"),  # type: ignore
            model_api_key=get_value(bot_config, default_config["bot"], "model_api_key"),  # type: ignore
            model_api_url=get_value(bot_config, default_config["bot"], "model_api_url"),  # type: ignore
            web_interface_port=int(get_value(web_interface_config, default_config["web_interface"], "web_interface_port")),  # type: ignore
            web_interface_api_key=get_value(web_interface_config, default_config["web_interface"], "web_interface_api_key"),  # type: ignore
            matrix_user_name=get_value(message_interface_config, default_config["message_interface"], "matrix_user_name"),  # type: ignore
            matrix_user_password=get_value(message_interface_config, default_config["message_interface"], "matrix_user_password"),  # type: ignore
            matrix_server=get_value(message_interface_config, default_config["message_interface"], "matrix_server"),  # type: ignore
        )

    def to_dict(self) -> ConfigDict:
        bot: BotConfigDict = {
            "bot_name": self.bot_name,
            "bot_timeout": self.bot_timeout,
            "model_name": self.model_name,
            "model_api_key": self.model_api_key,
            "model_api_url": self.model_api_url,
        }
        web_interface: WebInterfaceConfigDict = {
            "web_interface_port": self.web_interface_port,
            "web_interface_api_key": self.web_interface_api_key,
        }
        message_interface: MessageInterfaceConfigDict = {
            "matrix_user_name": self.matrix_user_name,
            "matrix_user_password": self.matrix_user_password,
            "matrix_server": self.matrix_server,
        }
        config: ConfigDict = {
            "id": self.id,
            "profile_name": self.bot_profile_name,
            "bot": bot,
            "web_interface": web_interface,
            "message_interface": message_interface,
        }
        return config


class Storage:
    bot_config: Config
    bot_memory: BotMemory

    def __init__(self):
        self.logger = setup_logger(
            "StorageManager",
            logging.DEBUG,
            max_bytes=2 * 1024 * 1024,
            backup_count=1,
        )
        current_dir = Path(__file__).parent
        grandparent_dir = current_dir.parent.parent
        self.config_path = grandparent_dir / "user/config.json"
        self.memory_path = grandparent_dir / "user/bot_memory.json"

        self.load_data()
        self.store_data()

    def load_data(self):
        """Load both config and memory data."""
        try:
            self.logger.info("Started loading bot config and memory")
            self._load_config()
            self._load_memory()
            self.logger.info("Done loading bot config and memory")
        except Exception as e:
            self.logger.exception(f"Failed to read bot config and memory: {e}")

    def store_data(self):
        """Store both config and memory data."""
        try:
            self._store_config()
            self._store_memory()
        except Exception as e:
            self.logger.exception(f"Failed store bot config and memory: {e}")

    def _load_config(self):
        """Load configuration from config.json."""
        if not self.config_path.is_file():
            self.logger.warning(
                f"Config file not found at {self.config_path}. Initializing empty config."
            )
            self.bot_config = Config.from_default()
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                config_data = json.load(f)
                self.bot_config = Config.from_dict(config_data)
                self.logger.info(
                    f"Config loaded successfully from {self.config_path}"
                )
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in config file: {e}")

    def _store_config(self):
        """Store configuration to config.json."""
        if self.bot_config is None:
            raise ValueError("bot_config is not loaded and cannot be stored.")

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.bot_config.to_dict(), f, indent=4)
            self.logger.info(
                f"Config stored successfully to {self.config_path}"
            )

    def _load_memory(self):
        """Load bot memory from bot_memory.json."""
        if not self.memory_path.is_file():
            self.logger.warning(
                f"Memory file not found at {self.memory_path}. Initializing empty memory."
            )
            self.bot_memory = BotMemory()
            return

        with open(self.memory_path, "r", encoding="utf-8") as f:
            try:
                memory_data = json.load(f)
                self.bot_memory = BotMemory.from_dict(memory_data)
                self.logger.info(
                    f"Bot memory loaded successfully from {self.memory_path}"
                )
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in memory file: {e}")

    def _store_memory(self):
        """Store bot memory to bot_memory.json."""
        if self.bot_memory is None:
            raise ValueError("bot_memory is not loaded and cannot be stored.")

        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.bot_memory.to_dict(), f, indent=4)
            self.logger.info(
                f"Bot memory stored successfully to {self.memory_path}"
            )
