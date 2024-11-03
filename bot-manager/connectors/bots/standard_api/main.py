import asyncio
import json
from enum import Enum
from typing import Literal, Tuple, TypedDict

import requests

from app.lib.connectors.connector_base import ConnectorBase
from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.messaging.room import ChatRoom
from app.lib.scheduler import WakeUpSchedule, WakeUpScheduleType
from app.lib.storage.bot_memory import Periods, Roles


class Connector(ConnectorBase):
    async def dream(self) -> None:
        """reorganize its data when idling, start training or whatever"""
        while True:
            if self.bot.should_dream.is_set():
                self.logger.info("I'm dreaming")
                await asyncio.sleep(20)
            else:
                await asyncio.sleep(20)

    ##
    ##  Callbacks
    ##
    async def new_message_callback(
        self, room: ChatRoom, message: ReceiveChatMessage
    ) -> None:
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.new_message_received.format(
                sender_id=message.sender_id,
                sender_name=message.sender_name,
                room_name=room.name,
                room_id=room.room_id,
                message=message.message,
            )
        )
        self.logger.info(
            f"new message received, room: {room.name} - from: {message.sender_name} - message: {message.message}"
        )

    async def on_scheduled_wakeup(self) -> None:
        await self._send_and_respond_to_model(
            message_content=(
                self.bot.profile.time_out_wakeup
                if self.scheduled_wakeup.type == WakeUpScheduleType.planned
                else self.bot.profile.no_activity
            )
        )

    async def on_startup(self):
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_initial_prompt(
                bot_name=self.bot.storage.bot_config.bot_name
            )
        )

    ##
    ##  commands that are used by the model
    ##

    async def _help(self):
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_initial_prompt(
                self.bot.storage.bot_config.bot_name
            )
        )

    async def _set_my_name(self, bot_name: str) -> None:
        if self.bot.storage.bot_config.bot_name:
            await self._send_and_respond_to_model(
                message_content=self.bot.profile.bot_name_already_exits
            )
        else:
            self.bot.storage.bot_config.bot_name = bot_name
            self.bot.storage.store_data()
            await self._get_my_name()

    async def _get_my_name(self) -> None:
        response: str
        if self.bot.storage.bot_config.bot_name:
            response = self.bot.profile.my_name.format(
                {"name": self.bot.storage.bot_config.bot_name}
            )
        else:
            response = (
                self.bot.storage.bot_config.bot_name
                or self.bot.profile.bot_name_not_set
            )
        await self._send_and_respond_to_model(message_content=response)

    async def _set_timeout(self, timeout: int) -> None:
        self.scheduled_wakeup = WakeUpSchedule(
            sleep_time=timeout, type=WakeUpScheduleType.planned
        )

    async def _send_message(
        self, message: str, room_id: str, user_id: str | None
    ):
        send_response: SendChatMessageResponse = await self.bot.send_message(
            message, room_id, user_id
        )
        if send_response.success:
            response = self.bot.profile.successfully_sent_message
        else:
            response = self.bot.profile.failed_to_send_message.format(
                error=send_response.error
            )
        await self._send_and_respond_to_model(message_content=response)

    async def _get_rooms_list(self):
        rooms = self.bot.get_rooms_list()
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_rooms_list.format(
                {"rooms", json.dumps(rooms)}
            )
        )

    async def _get_room_history(self, room_id: str, start: int, to: int):
        room_history = self.bot.get_room_history(room_id, start, to)
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_room_history.format(
                room_history=json.dumps(room_history)
            )
        )

    async def _get_users(self, room_id: str):
        room_history = self.bot.get_users(room_id)
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_users.format(
                room_history=json.dumps(room_history)
            )
        )

    async def _store_summary(
        self, interval: Periods, start_time: int, summary: str
    ):
        self.bot.storage.bot_memory.set_periodic_summary(
            interval, start_time, summary
        )
        self.bot.storage.store_data()
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.summary_stored
        )

    async def _store_mind_map(self, mind_map: str | None):
        self.bot.storage.bot_memory.mind_map = mind_map
        self.bot.storage.store_data()
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.mind_map_stored
        )

    async def _get_mind_map(self):
        response: str
        if self.bot.storage.bot_memory.mind_map:
            response = self.bot.storage.bot_memory.mind_map
        else:
            response = self.bot.profile.mind_map_empty
        await self._send_and_respond_to_model(message_content=response)

    async def _get_summary(self, interval: Periods, start_time: int):
        summary = self.bot.storage.bot_memory.get_periodic_summary(
            interval=interval, start_time=start_time
        )
        response: str
        if summary:
            response = summary.summary_text
        else:
            response = self.bot.profile.summary_empty
        await self._send_and_respond_to_model(message_content=response)

    async def _send_and_respond_to_model(
        self, message_content: str, role: Roles = Roles.SYSTEM
    ) -> Tuple[bool, str | None]:
        self.bot.scheduler.scheduled_wakeup = WakeUpSchedule(
            sleep_time=self.bot.storage.bot_config.bot_timeout,
            type=WakeUpScheduleType.planned,
        )
        self.bot.storage.bot_memory.add_message(
            role=role, content=message_content
        )
        self.logger.info(f"Sending new message to model: {message_content}")
        self.bot.storage.store_data()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bot.storage.bot_config.model_api_key}",
        }

        data = {
            "model": self.bot.storage.bot_config.model_name,
            "messages": [{"role": "user", "content": message_content}],
        }
        try:
            response = requests.post(
                self.bot.storage.bot_config.model_api_url,
                headers=headers,
                data=json.dumps(data),
            )

            if response.status_code == 200:
                model_response_json: ModelResponse = response.json()
                self.logger.info(
                    "Model response JSON:", json.dumps(model_response_json)
                )
                self.bot.storage.bot_memory.add_message(
                    role=Roles.ASSISTANT, content=model_response_json
                )

                return True, model_response_json
            else:
                self.logger.error(
                    f"Error response from from the model {self.bot.storage.bot_config.model_api_url} - Error: {response.status_code}, {response.text}"
                )
        except Exception as e:
            self.logger.exception(
                f"Error getting response from from the model {self.bot.storage.bot_config.model_api_url}: {e}"
            )
        return False, None


class ModelFinishReason(Enum):
    STOP = "stop"


class ModelResponseMessage(TypedDict):
    role: Roles
    content: str
    refusal: None


class ModelResponseChoices(TypedDict):
    index: int
    message: ModelResponseMessage

    logprobs: None
    finish_reason: ModelFinishReason


class ModelResponseUsage(TypedDict):
    total_tokens: int


class ModelResponse(TypedDict):
    id: str
    object: Literal['chat.completion']
    created: int
    model: str
    choices: list[ModelResponseChoices]
    usage: ModelResponseUsage
    system_fingerprint: str
