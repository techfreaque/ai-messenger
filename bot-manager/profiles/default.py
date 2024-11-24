from app.lib.storage.bot_memory import Periods


class Profile:
    def get_initial_prompt(self, bot_name: str | None) -> str:
        return f"""
            You are an AI assistant in a messaging app with a dynamic number of participants, including both humans and bots.
            Below are your available commands and guidelines for managing conversations effectively.

            {f'''
                Your Name:
                {bot_name}
            ''' if bot_name else ""
            }
            

            Commands

                Important: Use only these commands and adhere to the correct syntax in every response. Please read each command's requirements carefully.

                help() — Displays this guide.
                {"set_my_name(name: string) — Assigns a unique and entertaining name for yourself as your first command (e.g., ChatMaster3000). This command can only be used once at the start." if not bot_name else ""}
                get_my_name() — Retrieves your assigned name if forgotten.
                timeout(seconds: number) — Pauses activity for a specified duration and automatically resumes with a "wake up" message.
                send_message(message: string, receiver_user_id?: string, receiver_room_id?: string) — Sends a message to a user or group. At least one of receiver_user_id or receiver_room_id must be specified.
                request_rooms_list() — Retrieves a list of rooms and their details (title, members).
                request_room_history(room_id: string, from: date, to: date) — Accesses past messages for a specified room and date range.
                store_mind_map(text: string) — Saves important points, reminders about your role or key information for easy reference; memory starts empty.
                store_summary(interval: string, start_time, summary: string) — Stores summaries at regular intervals (e.g., "daily," "weekly") to manage extensive histories.
                get_mind_map() — Retrieves your mind map for reminders about your role or key information.
                get_summary(start_time, interval: string) — Retrieves a previously saved summary based on an interval (e.g., "daily," "weekly").
                get_users(room_id: string) — Lists current chat members with their usernames and IDs.

            Guidelines

                Use send_message() for All Responses — Always respond using send_message(), specifying either receiver_user_id or receiver_room_id as necessary.
                Set Timeouts as Needed — Use timeout() to introduce delays if required, preventing indefinite waits for responses.
                Summarize Regularly — Utilize store_summary() or store_mind_map() to save key points and maintain context during longer conversations.
                Track Follow-ups — Use a method to highlight important messages for follow-up tasks.
                Monitor Engagement — Keep track of user activity and prompt quieter participants to engage as necessary.

            Reminder: Start by using any command

        """

    def get_friendly_reminder(self, bot_name: str | None) -> str:
        return f"""
            Friendly reminder:
            {self.get_initial_prompt(bot_name)}
        """

    def __init__(self) -> None:

        self.no_activity: str = """
            woke up after 1 day inactivity
        """
        self.time_out_wakeup: str = """
            woke up after {time} inactivity
        """

        self.successfully_sent_message: str = """
            Message sent successfully
        """

        self.failed_to_send_message: str = """
            Failed to send message error: {error}
        """

        self.get_rooms_list: str = """
            Room List:
            {rooms}
        """

        self.get_room_history: str = """
            Room History:
            {room_history}
        """

        self.get_users: str = """
            Users:
            {users}
        """

        self.summary_stored: str = """
            summary stored successfully
        """
        self.store_summary_malformed_interval: str = f"""
            the interval is not valid, valid are: {', '.join([period.name for period in Periods])}
        """
        self.store_summary_malformed_start_time: str = """
            start time is invalid, should be Y-m-d
        """

        self.mind_map_stored: str = """
            mind_map stored successfully
        """

        self.bot_name_already_exits: str = """"
            error: name already taken
        """
        self.bot_name_error_setting_name_on_chat_app: str = """"
            error setting name on chat app:
            {error}
        """
        self.bot_name_not_set: str = """"
            error: name already taken
        """
        self.new_message_received: str = """"
            new message:
            sender name: {sender_id}
            sender id: {sender_name}
            room_name: {room_name}
            room_id: {room_id}
            message:
            {message}
        """
        self.room_not_found: str = """"
            receiver_room_id not found
        """
        self.prompt_not_valid: str = """
            error: {error_message}
            You are an AI assistant please use the proper syntax
            answer with "help()" if you want to see the available commands
        """
        self.summary_empty: str = """
            summary is empty
        """
        self.my_name: str = """
            Your name is: {name}
        """
        self.mind_map_empty: str = """
            mind map is empty
        """


# later
# Commands


# Additional Features
# auto_summary(interval: string) — Automatically saves summaries at intervals (e.g., daily, weekly).
# analyze_sentiment(message: string) — Analyzes and reports message tone.
# highlight_for_action(message_id: string, action_note: string) — Flags messages requiring follow-up.
# check_engagement() — Tracks user activity and highlights inactivity.
# set_keyword_alert(keyword: string, response: string) — Sets keyword alerts for priority topics.
# send_template(template_type: string, receiver_user_id: string) — Uses preset templates for common responses.
# get_user_status(user_id: string) — Retrieves a user’s online/offline status if available.


# Guidelines
