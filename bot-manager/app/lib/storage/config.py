import logging
import uuid
from dataclasses import dataclass
from typing import Optional, TypedDict

from app.lib.logger import setup_logger


class ConfigDict(TypedDict):
    id: str
    profile_name: str
    bot: "BotConfigDict"
    web_interface: "WebInterfaceConfigDict"
    message_interface: "MessageInterfaceConfigDict"


class WebInterfaceConfigDict(TypedDict):
    web_interface_port: int
    web_interface_api_key: str


class BotConfigDict(TypedDict):
    bot_name: Optional[str]
    bot_timeout: int
    profile_file_name: str
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
    profile_file_name: str
    model_api_key: Optional[str]
    model_api_url: str
    model_name: str
    web_interface_port: int
    web_interface_api_key: str
    matrix_user_name: Optional[str]
    matrix_user_password: Optional[str]
    matrix_server: str

    @staticmethod
    def logger():
        return setup_logger(
            "ConfigManager",
            logging.DEBUG,
        )

    @classmethod
    def from_default(cls) -> "Config":
        return cls.from_dict(cls.get_default_config())

    @staticmethod
    def get_default_config() -> ConfigDict:
        bot: BotConfigDict = {
            "bot_name": None,
            "bot_timeout": 86400,  # one day
            "profile_file_name": "default",
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
            profile_file_name=get_value(bot_config, default_config["bot"], "profile_file_name"),  # type: ignore
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
            "profile_file_name": self.profile_file_name,
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
