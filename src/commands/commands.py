import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.chat_members import ChatMembers


async def start(chat_members: ChatMembers, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = chat_members.get_chat_ids()
    if update.effective_chat.id not in chat_ids:
        chat_members.add_user(update)
        reply_message = "Hi, I am your assistant for the appointments at SuperC Ausländeramt. I am now searching for the appointments for students. \
I check if there are any updates on the website every 2-4 minutes.\n\
/stop - if you want me to stop sending you updates.\n\
/restart - if you want me to restart, after you've stopped me.\n\
I hope I will be able to help you:)"
    else:
        reply_message = "Hey, I think we've already met :)\nIf you want to know what I can do, please write /help"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = "Here is what you need to know: \
I check if there are any updates on the website every 2-4 minutes.\n\
/stop - if you want me to stop sending you updates.\n\
/restart - if you want me to restart, after you've stopped me.\n\
I hope I will be able to help you:)"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


async def restart(chat_members: ChatMembers, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = chat_members.get_chat_ids()
    if update.effective_chat.id not in chat_ids.keys():
        chat_members.add_user(update)
    if chat_ids[update.effective_chat.id]:
        reply_message = "I'm already working on it for you"
    else:
        chat_ids[update.effective_chat.id] = True
        reply_message = "Thanks, now I am checking every 2-4 minutes for new appointments. As soon as I will find anything, I will let you know😉"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


async def stop(chat_members: ChatMembers, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = chat_members.get_chat_ids()
    chat_ids[update.effective_chat.id] = False
    logging.info(f"{update.effective_chat.first_name} wanted to stop:(")
    reply_message = "I will not be sending you any updates to this topic anymore😢"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


async def start_admin_update(chat_members: ChatMembers, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = chat_members.get_chat_ids()
    message = "I am now in the process of the update, so I might not be working for a while\nI will tell you when my software is up to date:)"
    for id in chat_ids.keys():
        context.bot.send_message(chat_id=id, text=message)


async def finish_admin_update(chat_members: ChatMembers, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = chat_members.get_chat_ids()
    message = "I am finished with the update, so I am back to work:)"
    for id in chat_ids.keys():
        context.bot.send_message(chat_id=id, text=message)
