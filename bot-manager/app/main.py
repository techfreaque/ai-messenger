from app.lib.bot_manager import BotManager


def main() -> None:
    bot = BotManager()
    bot.init_web_server()
    bot.start_all_bot_connectors()
    # bot.start_dreaming()
    bot.watch_wakeup_schedule()
    bot.start_web_server()
