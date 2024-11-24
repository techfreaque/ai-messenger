from app.lib.bot_manager import BotManager


def main(dev_mode: bool) -> None:
    bot = BotManager(dev_mode=dev_mode)
    # bot.run_startup_tasks()
    bot.scheduler.start_scheduler()
    bot.web_server.start_web_server()
