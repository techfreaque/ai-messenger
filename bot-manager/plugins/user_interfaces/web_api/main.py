from app.lib.plugins.plugin_base import PluginBase


class Plugin(PluginBase):
    def api(self) -> None:
        @self.bot.web_server.app.route(
            '/',
        )
        def send_message() -> dict[str, bool]:  # type: ignore
            return {"yaaay": True}
