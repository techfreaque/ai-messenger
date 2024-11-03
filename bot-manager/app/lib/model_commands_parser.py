import datetime
import logging
import re
from typing import Awaitable, Callable

from app.lib.logger import setup_logger
from app.lib.storage.bot_memory import Periods


class ModelCommandsParser:
    logger = setup_logger(
        "Scheduler",
        logging.DEBUG,
    )

    @staticmethod
    def parse_interval(period: str) -> Periods | None:
        try:
            return Periods(period)
        except ValueError:
            return None

    @staticmethod
    def parse_date(start_time: str) -> int | None:
        try:
            return int(
                datetime.datetime.strptime(start_time, "%Y-%m-%d").timestamp()
            )
        except ValueError:
            return None

    async def parse_command(
        self, command: str, on_command_not_valid: Callable[[], Awaitable[None]]
    ) -> None:
        command_pattern = re.compile(r'(\w+)\((.*)\)')
        match = command_pattern.match(command)
        if not match:
            await on_command_not_valid()
            return

        command_name, args = match.groups()
        args_dict = {}
        if args:
            args = args.split(',')
            for arg in args:
                key, value = arg.split('=')
                args_dict[key.strip()] = value.strip().strip('"')

        command_method = getattr(self, f'_{command_name}', None)
        if command_method:
            try:
                return await command_method(**args_dict)
            except Exception as e:
                self.logger.exception(
                    f"Failed to execute command from model, error: {e}"
                )
        else:
            await on_command_not_valid()
            return
