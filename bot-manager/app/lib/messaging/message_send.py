from enum import Enum


class SendChatMessageResponse:
    def __init__(self, success: bool, error: str | None):
        self.success: bool = success
        self.error: str | None = error


class SendMessageType(Enum):
    TEXT = "m.text"
