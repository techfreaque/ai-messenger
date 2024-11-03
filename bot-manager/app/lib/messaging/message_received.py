from dataclasses import dataclass


@dataclass
class ReceiveChatMessage:
    sender_id: str
    sender_name: str
    message: str
