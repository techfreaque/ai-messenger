from app.lib.connector_base import ConnectorBase


class Connector(ConnectorBase):
    def api(self) -> None:
        @self.bot.app.route(
            '/',
        )
        def send_message() -> dict[str, bool]:  # type: ignore
            return {"yaaay": True}
