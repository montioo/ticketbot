# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

# Vielleicht zu GitHub:
# http://docs.python-guide.org/en/latest/writing/structure/

# Vielleicht mit requests
# http://docs.python-requests.org/en/master/user/quickstart/

import telegram
from telegram.error import NetworkError, Unauthorized
from telegram.ext import Updater
from time import sleep

import threading

import xmlDatabase as xmlDb
import utility as util

updater = Updater(token='_BOT_TOKEN_HERE__SEE_TELEGRAM_BOT_MANUAL_')
bot = updater.bot


def notify_clients(msg):
    client_notifier = Notify('users', msg)
    client_notifier.start()


def notify_client(msg, chat_id):
    client_notifier = Notify(chat_id, msg)
    client_notifier.start()


def notify_admins(msg):
    admin_msg = "<b>admin_info:</b>\n" + msg
    admin_notifier = Notify('admins', admin_msg)
    admin_notifier.start()


class Notify(threading.Thread):
    def __init__(self, user_group, msg):
        threading.Thread.__init__(self)
        self.user_group = user_group
        self.msg = msg

    def is_chat_id(self):
        try:
            int(self.user_group)
            return True
        except ValueError:
            return False

    def run(self):
        if self.is_chat_id():
            bot.send_message(chat_id=int(self.user_group), text=self.msg, parse_mode=telegram.ParseMode.HTML)
        else:
            clients = xmlDb.get_users(self.user_group)
            for client in clients:
                bot.sendMessage(chat_id=int(client), text=self.msg, parse_mode=telegram.ParseMode.HTML)


def launch_cmd_handler(handler):
    cmd_handl = CommandHandler(handler)
    cmd_handl.daemon = True
    cmd_handl.start()


class CommandHandler(threading.Thread):
    def __init__(self, handlers):
        threading.Thread.__init__(self)
        self.handlers = handlers
        self.update_id = None

    def run(self):
        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            self.update_id = bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None

        while True:
            try:
                self.respond()
            except NetworkError:
                sleep(1)
            except Unauthorized:
                # The user has removed or blocked the bot.
                self.update_id += 1
            except Exception as e:
                print("--- UNEXPECTED TELEGRAM ERROR ---")
                print(util.get_time_string())
                print(e)

    def respond(self):
        # Request updates after the last update_id
        for update in bot.get_updates(offset=self.update_id, timeout=10):
            self.update_id = update.update_id + 1

            if update.message:  # bot can receive updates without messages
                if not xmlDb.user_exists('blacklist', str(update.message.chat_id)):
                    answer = self.choose_handler(update.message.text, str(update.message.chat_id))
                    # print(answer)
                    if answer != "":
                        update.message.reply_text(answer, parse_mode=telegram.ParseMode.HTML)

    def choose_handler(self, msg, chat_id):
        cmds = msg.split(None, 1)  # Teilt String an erstem Newline oder Space
        console_out = util.get_time_string() + ": telegramMsgCmd:\n"
        console_out += "  chat_id: " + chat_id + "\n"
        console_out += "  nachricht: " + msg
        print(console_out)
        if cmds[0][0] == '/':
            cmd = cmds[0][1:]
            if cmd in self.handlers:
                # dict mit Handlerfunktionen
                args = cmds[1] if len(cmds) == 2 else ""
                return self.handlers[cmd](args, chat_id)

        return ""
