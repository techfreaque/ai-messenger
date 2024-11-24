import datetime
import logging
import re
import shlex
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Awaitable, Callable

from app.lib.logger import setup_logger
from app.lib.storage.bot_memory import Periods

if TYPE_CHECKING:
    from plugins.bots.standard_api.main import Plugin


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

    def _extract_command(self, command: str) -> tuple[str, str] | None:
        # Improved regex to handle nested parentheses and quotes
        command_pattern = re.compile(r'^(\w+)\s*\(([\s\S]*)\)$')
        match = command_pattern.match(command.strip())
        if match:
            return match.group(1), match.group(2)
        return None

    def _parse_arguments(self, args: str) -> tuple[list[str], dict[str, str]]:
        args_dict: dict[str, str] = {}
        positional_args: list[str] = []
        if args:
            lexer = shlex.shlex(args, posix=True)
            lexer.whitespace_split = True
            lexer.whitespace = ','
            lexer.escape = ''
            tokens = list(lexer)
            for token in tokens:
                if '=' in token:
                    key, value = token.split('=', 1)
                    args_dict[key.strip()] = value.strip()
                else:
                    positional_args.append(token.strip())
        return positional_args, args_dict

    async def parse_command(
        self,
        plugin: "Plugin",
        command: str,
        on_command_not_valid: Callable[[str], Awaitable[None]],
    ) -> None:
        error_message: str | None = None
        try:
            # Step 1: Strip markdown code fences if present
            code_fence_pattern = re.compile(
                r'```(?:\w+)?\n([\s\S]+?)\n```', re.MULTILINE
            )
            code_fence_match = code_fence_pattern.search(command)
            if code_fence_match:
                command = code_fence_match.group(1).strip()
                self.logger.debug("Extracted command from code fence.")

            # Step 2: Extract the command name and arguments
            extracted = self._extract_command(command)
            if not extracted:
                error_message = "Command pattern did not match."
                self.logger.warning(error_message)
                await on_command_not_valid(error_message)
                return
            command_name, args = extracted

            # Step 3: Parse the arguments
            positional_args, args_dict = self._parse_arguments(args)

            # Step 4: Retrieve the command method dynamically
            command_method = getattr(plugin, f'_{command_name}', None)
            if command_method:
                # Determine if the method accepts positional arguments
                sig = signature(command_method)
                has_var_positional = any(
                    p.kind == Parameter.VAR_POSITIONAL
                    for p in sig.parameters.values()
                )

                if has_var_positional:
                    self.logger.debug(
                        f"Invoking '{command_name}' with positional and keyword arguments."
                    )
                    return await command_method(*positional_args, **args_dict)
                # TODO handle positional_args:
                if positional_args:
                    # Map positional arguments to the method's parameters
                    bound_args: dict[str, str] = {}
                    method_params = sig.parameters
                    # Exclude parameters that are already provided via keyword arguments
                    remaining_params = [
                        p
                        for p in method_params.values()
                        if p.name not in args_dict
                        and p.kind
                        in (
                            Parameter.POSITIONAL_ONLY,
                            Parameter.POSITIONAL_OR_KEYWORD,
                        )
                    ]

                    if len(positional_args) > len(remaining_params):
                        error_message = (
                            f"Too many positional arguments for command '{command_name}'. "
                            + f"Expected at most {len(remaining_params)}, got {len(positional_args)}."
                        )
                        self.logger.warning(error_message)
                        await on_command_not_valid(error_message)
                        return

                    for arg_value, param in zip(
                        positional_args, remaining_params
                    ):
                        bound_args[param.name] = arg_value
                        self.logger.info(
                            f"Assigned positional argument '{arg_value}' to parameter '{param.name}'."
                        )

                    # Combine bound positional arguments with keyword arguments
                    combined_args = {**bound_args, **args_dict}

                    # Check for missing required parameters
                    missing_params = [
                        p.name
                        for p in method_params.values()
                        if p.default is Parameter.empty
                        and p.name not in combined_args
                        and p.kind
                        not in (
                            Parameter.VAR_POSITIONAL,
                            Parameter.VAR_KEYWORD,
                        )
                    ]

                    if missing_params:
                        error_message = f"Missing required arguments for command '{command_name}': {missing_params}"
                        self.logger.warning(error_message)
                        await on_command_not_valid(error_message)
                        return

                    self.logger.debug(
                        f"Invoking '{command_name}' with : {combined_args}"
                    )
                    return await command_method(**combined_args)
                # No positional arguments; invoke with keyword arguments
                self.logger.debug(
                    f"Invoking '{command_name}' with keyword arguments: {args_dict}"
                )
                await command_method(**args_dict)
                return
            error_message = f"No method found for command '{command_name}'."
            self.logger.warning(error_message)
            await on_command_not_valid(error_message)
            return

        except Exception as e:
            error_message = f"Failed to execute command from model, error: {e}"
            self.logger.exception(error_message)
            await on_command_not_valid(error_message)
            return
