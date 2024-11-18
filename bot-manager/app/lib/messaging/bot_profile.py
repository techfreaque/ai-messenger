from dataclasses import dataclass


@dataclass
class SetUserNameResponse:
    name: str
    error_message: str | None
