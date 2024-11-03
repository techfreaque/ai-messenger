from app.lib.connectors.connector_base import ConnectorBase


class Connector(ConnectorBase):
    def api(self) -> None:
        @self.bot.web_server.app.route(
            '/',
        )
        def send_message() -> dict[str, bool]:  # type: ignore
            return {"yaaay": True}
