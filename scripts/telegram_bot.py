import logging
import click

from functools import partial
from telegram.ext import ApplicationBuilder, CommandHandler

from src.chat_members import ChatMembers
from src import CheckAppointmentsTask, ScheduleTask
from src.commands.commands import start, help, restart, stop, start_admin_update, finish_admin_update


@click.command()
@click.option("--bot-type", default="RWTH", help="Type of the bot: RWTH or CIT.")
def main(bot_type: str):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        # filename = "log.log"
    )

    bot_token = ""
    chat_members = ChatMembers()

    application = ApplicationBuilder().token(bot_token).build()

    start_handler = CommandHandler("start", partial(start, chat_members))
    application.add_handler(start_handler)

    help_handler = CommandHandler("help", help)
    application.add_handler(help_handler)

    restart_handler = CommandHandler("restart", partial(restart, chat_members))
    application.add_handler(restart_handler)

    stop_handler = CommandHandler("stop", partial(stop, chat_members))
    application.add_handler(stop_handler)

    start_admin_update_handler = CommandHandler("start_admin_update", partial(start_admin_update, chat_members))
    application.add_handler(start_admin_update_handler)

    finish_admin_update_handler = CommandHandler("finish_admin_update", partial(finish_admin_update, chat_members))
    application.add_handler(finish_admin_update_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.info("Starting a bot")

    schedule_task = ScheduleTask(bot=application.bot, chat_members=chat_members)
    schedule_task.start()

    check_task = CheckAppointmentsTask(bot=application.bot, chat_members=chat_members, bot_type=bot_type)
    check_task.start()

    application.run_polling()


if __name__ == "__main__":
    main()
