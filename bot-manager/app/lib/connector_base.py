from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from nio import MatrixRoom, RoomMessageText

from app.lib.logger import setup_logger

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class ConnectorBase:
    """
    Protocol for connector classes. All connectors must implement this
    """

    def __init__(self, bot: BotManager):
        self.bot: BotManager = bot
        current_script_path = Path(__file__).resolve()

        # Get the parent directory path
        parent_dir_path = current_script_path.parent

        # Extract the parent folder name
        current_folder_name = parent_dir_path.name
        self.logger = setup_logger(
            "Connector" + current_folder_name,
            logging.DEBUG,
            max_bytes=2 * 1024 * 1024,
            backup_count=1,
        )

    async def on_startup(
        self,
    ):
        """
        This gets called on startup
        """

    async def on_scheduled_wakeup(
        self,
    ):
        """
        This gets called when the sleep timeout is reached or if a wakeup was scheduled
        """

    async def new_message_callback(
        self, room: MatrixRoom, event: RoomMessageText
    ):
        """
        This gets called when a new message comes in from a messaging connector
        """

    def api(
        self,
    ):
        """
        Add your web apis here
        """
