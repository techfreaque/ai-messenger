import os
from typing import TYPE_CHECKING

from flask import Response, redirect, send_from_directory

from app.lib.bot_manager import BotManager
from app.lib.plugins.plugin_base import PluginBase

if TYPE_CHECKING:
    from app.lib.webserver.webserver import WebServer


class Plugin(PluginBase):
    REACT_BUILD_Folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "frontend/build"
    )
    REACT_BUILD_FILE = "index.html"

    def __init__(self, bot: "BotManager", plugin_name: str):
        super().__init__(bot, plugin_name)

    def api(self) -> None:
        web_server: "WebServer" = self.bot.web_server
        path_prefix = "/web"

        # Route to serve React frontend
        @web_server.app.route('/')
        def home_redirect():  # type: ignore
            return redirect(f'{path_prefix}')

        @web_server.app.route(f'{path_prefix}/')
        @web_server.app.route(f'{path_prefix}/<path:path>')
        def serve_react(path: str | None = None) -> Response:  # type: ignore
            if path and os.path.exists(
                os.path.join(self.REACT_BUILD_Folder, path)
            ):
                return send_from_directory(self.REACT_BUILD_Folder, path)
            return send_from_directory(
                self.REACT_BUILD_Folder, self.REACT_BUILD_FILE
            )
