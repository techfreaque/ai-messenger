import asyncio
import datetime
import json
import re
from enum import Enum
from typing import Literal, Tuple, TypedDict

import requests

from app.lib.messaging.message_received import ReceiveChatMessage
from app.lib.messaging.message_send import SendChatMessageResponse
from app.lib.model_commands_parser import ModelCommandsParser
from app.lib.plugins.plugin_base import PluginBase
from app.lib.scheduler import WakeUpSchedule, WakeUpScheduleType
from app.lib.storage.bot_memory import Roles


class Plugin(PluginBase):
    parser: ModelCommandsParser = ModelCommandsParser()

    async def dream(self) -> None:
        while self.bot.scheduler.should_dream.is_set():
            self.logger.info("I'm dreaming")
            await asyncio.sleep(20)

    ##
    ##  Callbacks
    ##
    async def new_message_callback(self, message: ReceiveChatMessage) -> None:
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.new_message_received.format(
                sender_id=message.sender_id,
                sender_name=message.sender_name,
                room_name=message.room_name,
                room_id=message.room_id,
                message=message.message,
            )
        )
        self.logger.info(
            f"new message received, room: {message.room_name} - from: {message.sender_name} - message: {message.message}"
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
                name=self.bot.storage.bot_config.bot_name
            )
        else:
            response = self.bot.profile.bot_name_not_set
        await self._send_and_respond_to_model(message_content=response)

    async def _timeout(self, seconds: int) -> None:
        self.scheduled_wakeup = WakeUpSchedule(
            sleep_time=seconds, type=WakeUpScheduleType.planned
        )

    async def _send_message(
        self,
        message: str,
        receiver_room_id: str,
        receiver_user_id: str | None = None,
    ):
        send_response: SendChatMessageResponse = await self.bot.send_message(
            message=message, room_id=receiver_room_id, user_id=receiver_user_id
        )
        if send_response.success:
            response = self.bot.profile.successfully_sent_message
        else:
            response = self.bot.profile.failed_to_send_message.format(
                error=send_response.error
            )
        await self._send_and_respond_to_model(message_content=response)

    async def _request_rooms_list(self):
        rooms = self.bot.get_rooms_list()
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_rooms_list.format(
                rooms=json.dumps(rooms)
            )
        )

    async def _request_room_history(
        self, room_id: str, from_date: str, to_date: str
    ):
        _from_date = int(
            datetime.datetime.strptime(from_date, "%Y-%m-%d").timestamp()
        )
        _to_date = int(
            datetime.datetime.strptime(to_date, "%Y-%m-%d").timestamp()
        )
        room_history = self.bot.get_room_history(
            room_id, start=_from_date, to=_to_date
        )
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_room_history.format(
                room_history=json.dumps(room_history)
            )
        )

    async def _get_users(self, room_id: str):
        users = self.bot.get_users(room_id)
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.get_users.format(
                users=json.dumps(users)
            )
        )

    async def _store_summary(
        self, interval: str, start_time: str, summary: str
    ):
        _interval = self.parser.parse_interval(interval)
        _start_time = self.parser.parse_date(start_time)
        response: str
        if not _interval:
            response = self.bot.profile.store_summary_malformed_interval

        elif not _start_time:
            response = self.bot.profile.store_summary_malformed_start_time
        else:
            self.bot.storage.bot_memory.set_periodic_summary(
                interval=_interval, start_time=_start_time, summary=summary
            )
            self.bot.storage.store_data()
            response = self.bot.profile.summary_stored
        await self._send_and_respond_to_model(message_content=response)

    async def _store_mind_map(self, text: str):
        self.bot.storage.bot_memory.mind_map = text
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

    async def _get_summary(self, interval: str, start_time: str):
        _interval = self.parser.parse_interval(interval)
        _start_time = self.parser.parse_date(start_time)
        response: str
        if not _interval:
            response = self.bot.profile.summary_malformed_interval

        elif not _start_time:
            response = self.bot.profile.summary_malformed_start_time
        else:
            summary = self.bot.storage.bot_memory.get_periodic_summary(
                interval=_interval, start_time=_start_time
            )
            if summary:
                response = summary.summary_text
            else:
                response = self.bot.profile.summary_empty
        await self._send_and_respond_to_model(message_content=response)

    # async def _auto_summary(self, interval: str):
    #     # Implementation for auto_summary
    #     pass

    # async def _analyze_sentiment(self, message: str):
    #     # Implementation for analyze_sentiment
    #     pass

    # async def _highlight_for_action(self, message_id: str, action_note: str):
    #     # Implementation for highlight_for_action
    #     pass

    # async def _check_engagement(self):
    #     # Implementation for check_engagement
    #     pass

    # async def _set_keyword_alert(self, keyword: str, response: str):
    #     # Implementation for set_keyword_alert
    #     pass

    # async def _send_template(self, template_type: str, receiver_user_id: str):
    #     # Implementation for send_template
    #     pass

    # async def _get_user_status(self, user_id: str):
    #     # Implementation for get_user_status
    #     pass

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
                model_response: ModelResponseDict = response.json()
                self.logger.info(
                    "Model response JSON:", json.dumps(model_response)
                )
                message: str = model_response["choices"][0]["message"]
                self.bot.storage.bot_memory.add_message(
                    role=Roles.ASSISTANT, content=message
                )
                await self.parser.parse_command(
                    message, self._on_command_not_valid
                )

                return True, message
            else:
                self.logger.error(
                    f"Error response from from the model {self.bot.storage.bot_config.model_api_url} - Error: {response.status_code}, {response.text}"
                )
        except Exception as e:
            self.logger.exception(
                f"Error getting response from from the model {self.bot.storage.bot_config.model_api_url}: {e}"
            )
        return False, None

    async def _on_command_not_valid(self):
        await self._send_and_respond_to_model(
            message_content=self.bot.profile.prompt_not_found
        )


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


class ModelResponseDict(TypedDict):
    id: str
    object: Literal['chat.completion']
    created: int
    model: str
    choices: list[ModelResponseChoices]
    usage: ModelResponseUsage
    system_fingerprint: str
