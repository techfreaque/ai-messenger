import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from flask import Flask
from flask_cors import CORS

from app.lib.logger import setup_logger
from app.lib.webserver.login import WebLoginManager

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class WebServer:
    def __init__(self, bot: "BotManager", dev_mode: bool) -> None:
        self.bot: "BotManager" = bot
        self.logger = setup_logger(
            "WebServer",
            logging.DEBUG,
        )
        app: Flask = Flask(__name__)
        app.secret_key = 'supersecretkey'
        CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

        # Session Configuration
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
        app.config['SESSION_COOKIE_SECURE'] = True  # Needed for SameSite=None
        app.config['SESSION_PERMANENT'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
        self.app: Flask = app
        self.login_manager: WebLoginManager = WebLoginManager(dev_mode)

    def start_web_server(
        self,
    ) -> None:
        self.logger.info(
            f"Starting web server on port: {self.bot.storage.bot_config.web_interface_port}"
        )
        self.login_manager.init_login(self.bot)
        self.init_web_server_plugins()
        self.app.run(
            host="0.0.0.0",
            port=self.bot.storage.bot_config.web_interface_port,
            debug=False,
        )

    def init_web_server_plugins(self) -> None:
        """
        Initializes plugins with api's
        """
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        for name, plugin in self.bot.plugin_manager.plugins.items():
            if self.bot.plugin_manager.is_overridden(plugin, "api"):
                self.logger.info(f"Starting api plugin {name}...")
                try:
                    plugin.api()
                    self.logger.info(f"Started api plugin {name}...")
                except Exception as e:
                    self.logger.exception(
                        f"Failed to start api on {name} plugin, error: {e}"
                    )
