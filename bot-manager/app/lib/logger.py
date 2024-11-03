import logging
import logging.handlers
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log messages based on their severity level.
    Also colors stack traces if present.
    """

    # Define colors for different log levels
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record): # type: ignore
        """
        Override the default format method to inject colors into the log messages and stack traces.
        """
        # Get the base formatted message
        formatted = super().format(record)
        # Get the color based on the log level
        log_color = self.COLORS.get(record.levelno, Fore.WHITE)

        if record.exc_info:
            # If there is exception information, color both the message and the stack trace
            # Split the formatted message into the main log and the exception
            parts = formatted.split('\n', 1)
            main_msg = parts[0]
            exc_msg = parts[1] if len(parts) > 1 else ''
            # Apply color to both parts
            colored_main = f"{log_color}{main_msg}{Style.RESET_ALL}"
            colored_exc = (
                f"{log_color}{exc_msg}{Style.RESET_ALL}" if exc_msg else ''
            )
            return f"{colored_main}\n{colored_exc}"
        else:
            # If no exception, color the entire formatted message
            return f"{log_color}{formatted}{Style.RESET_ALL}"


def setup_logger(
    name: str,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Sets up a logger with colored console output and file logging with rotation.
    Always uses the log file path '../../logs/log.txt'.

    :param name: Name of the logger.
    :param level: Logging level.
    :return: Configured logger.
    """
    max_bytes: int = 5 * 1024 * 1024  # 5 MB
    backup_count: int = 1
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = (
        False  # Prevent log messages from being propagated to the root logger
    )

    # Check if handlers are already added to prevent duplicate logs
    if not logger.handlers:
        # Define the fixed log file path
        # Calculate the absolute path relative to the current script
        script_dir = Path(__file__).parent.resolve()
        log_file_path = script_dir / '../../user/logs/log.txt'
        log_file_path = log_file_path.resolve()

        # Ensure the log directory exists
        log_dir = log_file_path.parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created log directory at: {log_dir}")
            except Exception as e:
                print(f"Failed to create log directory {log_dir}: {e}")
                raise

        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8',
            )
        except Exception as e:
            print(f"Failed to create file handler for {log_file_path}: {e}")
            raise

        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
