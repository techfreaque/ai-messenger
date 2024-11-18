import json
import logging
from pathlib import Path
from typing import TypedDict

from app.lib.logger import setup_logger
from app.lib.storage.bot_memory import BotMemory, BotMemoryDict
from app.lib.storage.config import Config, ConfigDict


class StorageDict(TypedDict):
    bot_config: ConfigDict
    bot_memory: BotMemoryDict


class Storage:
    bot_config: Config
    bot_memory: BotMemory

    def __init__(self):
        self.logger = setup_logger(
            "StorageManager",
            logging.DEBUG,
        )
        current_dir = Path(__file__).parent
        grandparent_dir = current_dir.parent.parent.parent
        self.config_path = grandparent_dir / "user/config.json"
        self.memory_path = grandparent_dir / "user/bot_memory.json"

        self.load_data()
        self.store_data()

    def to_dict(self) -> StorageDict:
        return {
            "bot_config": self.bot_config.to_dict(),
            "bot_memory": self.bot_memory.to_dict(),
        }

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
            self.logger.exception(f"Failed to store bot config and memory: {e}")

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
