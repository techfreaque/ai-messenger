from typing import TYPE_CHECKING, Tuple, Union

from flask import Response, jsonify, request

from app.lib.plugins.plugin_base import PluginBase
from app.lib.storage.storage import StorageDict

if TYPE_CHECKING:
    from app.lib.webserver.webserver import WebServer


class Plugin(PluginBase):
    def api(self) -> None:
        web_server: "WebServer" = self.bot.web_server
        path_prefix = "/api"

        @web_server.app.route(f'{path_prefix}/config', methods=['GET'])
        @web_server.login_manager.conditional_login_required()
        def get_config() -> tuple[StorageDict, int]:  # type: ignore
            print("Getting config: " + str(self.bot.storage.to_dict()))
            return self.bot.storage.to_dict(), 200

        @web_server.app.route(f'{path_prefix}/config', methods=['PUT'])
        @web_server.login_manager.conditional_login_required()
        def update_config() -> Tuple[Union[StorageDict, Response], int]:  # type: ignore
            data = request.json
            if not isinstance(data, dict):  # Type check for data
                return jsonify({"error": "Invalid data format"}), 400
            for key, value in data.items():
                setattr(bot_config, key, value)
            print("Updated config:", bot_config)
            return self.bot.storage.to_dict(), 200

        @web_server.app.route(f'{path_prefix}/config', methods=['POST'])
        @web_server.login_manager.conditional_login_required()
        def create_config() -> tuple[StorageDict, int]:  # type: ignore
            # TODO setup config
            return self.bot.storage.to_dict(), 200

        @web_server.app.route(f'{path_prefix}/config', methods=['DELETE'])
        @web_server.login_manager.conditional_login_required()
        def delete_config() -> tuple[StorageDict, int]:  # type: ignore
            # TODO delete config
            return self.bot.storage.to_dict(), 200
