from app.lib.bot_manager import BotManager


def main() -> None:
    bot = BotManager()
    bot.run_startup_tasks()
    # bot.start_dreaming()
    bot.scheduler.start_wakeup_scheduler()
    bot.web_server.start_web_server()
