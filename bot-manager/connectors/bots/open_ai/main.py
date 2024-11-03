import asyncio
import json
from typing import Tuple

from nio import MatrixRoom, RoomMessageText

from app.lib.connector_base import ConnectorBase
from app.lib.scheduler import WakeUpSchedule, WakeUpScheduleType
from app.lib.storage import Roles


class Connector(ConnectorBase):
    async def dream(self) -> None:
        """reorganize its data when idling, start training or whatever"""
        while True:
            if self.bot.should_dream.is_set():
                self.logger.info("I'm dreaming")
                await asyncio.sleep(20)
            else:
                await asyncio.sleep(20)

    async def new_message_callback(
        self, room: MatrixRoom, event: RoomMessageText
    ) -> None:
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.new_message_received.format(
                {
                    "sender_id": event.sender_key,
                    "sender_name": event.sender,
                    "room_name": room.name,
                    "room_id": room.room_id,
                    "message": event.formatted_body,
                }
            )
        )
        self.logger.info(f"new message received, room: {room} - event: {event}")

    async def on_scheduled_wakeup(self) -> None:
        await self.send_and_respond_to_model(
            message_content=(
                self.bot.profile.time_out_wakeup
                if self.scheduled_wakeup.type == WakeUpScheduleType.planned
                else self.bot.profile.no_activity
            )
        )

    async def on_startup(self):
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.get_initial_prompt(
                bot_name=self.bot.storage.bot_config.bot_name
            )
        )

    async def help(self):
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.get_initial_prompt(
                self.bot.storage.bot_config.bot_name
            )
        )

    async def set_my_name(self, bot_name: str) -> None:
        if self.bot.storage.bot_config.bot_name:
            await self.send_and_respond_to_model(
                message_content=self.bot.profile.bot_name_already_exits
            )
        else:
            self.bot.storage.bot_config.bot_name = bot_name
            self.bot.storage.store_data()
            await self.get_my_name()

    async def get_my_name(self) -> None:
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
        await self.send_and_respond_to_model(message_content=response)

    async def set_timeout(self, timeout: int) -> None:
        self.scheduled_wakeup = WakeUpSchedule(
            sleep_time=timeout, type=WakeUpScheduleType.planned
        )

    async def send_message(
        self, message: str, room_id: str, user_id: str | None
    ):
        success, error = self.bot.send_message(message, room_id, user_id)
        if success:
            response = self.bot.profile.successfully_sent_message
        else:
            response = self.bot.profile.failed_to_send_message.format(
                {"error": error}
            )
        await self.send_and_respond_to_model(message_content=response)

    async def get_rooms_list(self):
        rooms = self.bot.get_rooms_list()
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.get_rooms_list.format(
                {"rooms", json.dumps(rooms)}
            )
        )

    async def get_room_history(self, room_id: str, start: str, to: str):
        room_history = self.bot.get_room_history(room_id, start, to)
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.get_room_history.format(
                {"room_history", json.dumps(room_history)}
            )
        )

    async def get_users(self, room_id: str):
        room_history = self.bot.get_users(room_id)
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.get_users.format(
                {"room_history", json.dumps(room_history)}
            )
        )

    async def store_summary(self, interval: str, start_time: str, summary: str):
        self.bot.storage.bot_memory.set_periodic_summary(
            interval, start_time, summary
        )
        self.bot.storage.store_data()
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.summary_stored
        )

    async def store_mind_map(self, mind_map: str | None):
        self.bot.storage.bot_memory.mind_map = mind_map
        self.bot.storage.store_data()
        await self.send_and_respond_to_model(
            message_content=self.bot.profile.mind_map_stored
        )

    async def get_mind_map(self):
        response: str
        if self.bot.storage.bot_memory.mind_map:
            response = self.bot.storage.bot_memory.mind_map
        else:
            response = self.bot.profile.mind_map_empty
        await self.send_and_respond_to_model(message_content=response)

    async def get_summary(self, interval: str, start_time: str):
        summary = self.bot.storage.bot_memory.get_periodic_summary(
            interval=interval, start_time=start_time
        )
        response: str
        if summary:
            response = summary.summary_text
        else:
            response = self.bot.profile.summary_empty
        await self.send_and_respond_to_model(message_content=response)

    async def send_and_respond_to_model(
        self, message_content: str
    ) -> Tuple[bool, str | None]:
        self.bot.scheduled_wakeup = WakeUpSchedule(
            sleep_time=self.bot.storage.bot_config.bot_timeout,
            type=WakeUpScheduleType.planned,
        )
        self.bot.storage.bot_memory.add_message(
            role=Roles.USER, content=message_content
        )
        self.bot.storage.store_data()
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": f"Bearer {self.bot.storage.bot_config.model_api_key}",
        # }

        # data = {
        #     "model": self.bot.storage.bot_config.model_name,
        #     "messages": [{"role": "user", "content": message_content}],
        # }
        # try:
        #     response = requests.post(
        #         self.bot.storage.bot_config.model_api_url,
        #         headers=headers,
        #         data=json.dumps(data),
        #     )

        #     if response.status_code == 200:
        #         model_response_json = response.json()
        #         self.logger.info("Model response JSON:", model_response_json)
        #         self.bot.storage.bot_memory.add_message(role="Assistant", content=model_response_json)

        #         return True, model_response_json
        #     else:
        #         self.logger.error(
        #             f"Error response from from the model {self.bot.storage.bot_config.model_api_url} - Error: {response.status_code}, {response.text}"
        #         )
        # except Exception as e:
        #     self.logger.exception(
        #         f"Error getting response from from the model {self.bot.storage.bot_config.model_api_url}: {e}"
        #     )
        return False, None
