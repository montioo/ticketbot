# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

# Vielleicht zu GitHub:
# http://docs.python-guide.org/en/latest/writing/structure/

# Vielleicht mit requests
# http://docs.python-requests.org/en/master/user/quickstart/

import logging
import time

from telegram.ext import CommandHandler
from telegram.ext import Updater

import pullWebsite
import xmlDatabase


logger = logging.getLogger(__name__)

def notifyAdmins(bot, msg):
    admin_chat_ids = xmlDatabase.getUsers('admins')

    msg = "ADMIN INFO:\n" + msg

    for i in admin_chat_ids:
        bot.sendMessage(chat_id=int(i), text=msg)


def notifyUsers_ticketavailable(bot, entrys):
    print("  Notify Users")
    user_chat_ids = xmlDatabase.getUsers('users')
    msg = "Tickets erhaeltlich!\n"

    for e in entrys:
        msg += e.title + " -> " + e.price + "\n"

    print("Tickets: ", len(entrys))

    msg += "\nhttps://t.co/W5y3pkxxbQ"

    for u in user_chat_ids:
        print("Send to ID: ", u)
        bot.sendMessage(chat_id=int(u), text=msg)


def start(bot, update):
    msg = "Splash Tickets Resell Alert Bot\n\n"
    msg += "Dieser Bot versendet Benachrichtigungen, sobald bei TixForGigs ein Ticket fuers Splash21 zum Wiederverkauf steht.\n\n"
    msg += "Benutzung:\n"
    msg += "/sub: Benachrichtigungen erhalten\n"
    msg += "/unsub: Keine Benachrichtigungen mehr erhalten\n"
    msg += "/help: Diese Infonachricht noch mal senden\n\n"
    msg += "2018, Marius Montebaur"

    bot.sendMessage(chat_id=update.message.chat_id, text=msg)


def sub(bot, update):
    xmlDatabase.addUser('users', str(update.message.chat_id))
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Du bekommst eine Nachricht, sobald neue Tickets zum Verkauf stehen :-)")

    admin_msg = "Neuer Abonnent, chat_id = " + str(update.message.chat_id)
    notifyAdmins(bot, admin_msg)


def unsub(bot, update):
    xmlDatabase.removeUser('users', str(update.message.chat_id))
    bot.sendMessage(chat_id=update.message.chat_id, text="Benachrichtigungen ausgeschaltet.")

    admin_msg = "Abo beendet, chat_id = " + str(update.message.chat_id)
    notifyAdmins(bot, admin_msg)


def error_handler (bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(token='516006726:AAE1BwwS16JEWz9JZktwfEUg0xfxiBMsKPk')
    bot = updater.bot

    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    startHandler = CommandHandler('start', start)
    dispatcher.add_handler(startHandler)
    helpHandler = CommandHandler('help', start)
    dispatcher.add_handler(helpHandler)
    subHandler = CommandHandler('sub', sub)
    dispatcher.add_handler(subHandler)
    unsubHandler = CommandHandler('unsub', unsub)
    dispatcher.add_handler(unsubHandler)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()

    oldlen = -1

    print("start")

    while True:
        time.sleep(15)
        print("checking...")
        entrys = pullWebsite.pullTixForGigs()
        print("oldlen: ", oldlen, ", len(entrys): ", len(entrys))
        if oldlen == -1:
            oldlen = len(entrys)

        if entrys:
            print("Tickets da")
            if len(entrys) < oldlen:
                oldlen = len(entrys)

            if len(entrys) != oldlen:
                oldlen = len(entrys)
                # Tickets erhaeltlich
                notifyUsers_ticketavailable(bot, entrys)
                # notifyAdmins(bot, "-> neue Tickets")
                print("------------------------> neue Tickets")


if __name__ == "__main__":
    main()
