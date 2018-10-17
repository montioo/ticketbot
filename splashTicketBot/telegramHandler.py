import xmlDatabase as xmlDb
import telegramMessenger as telegramMsg
import ticketBot as tB
from time import sleep


def start(_, chat_id):
    msg = "<b>splash Ticket Bot 🤖</b>\n\n"

    msg += "Dieser Bot versendet Benachrichtigungen, sobald bei "
    msg += "TixforGigs.com ein Ticket fürs splash21 zum Wiederverkauf steht.\n\n"

    msg += "Du kannst von diesem Bot nicht nur Nachrichten erhalten, "
    msg += "sondern ihn auch mit Befehlen steuern. Ein Befehl sieht immer so aus:\n"
    msg += "<code>/befehl</code>\n\n"

    msg += "/sub - Aktiviere Benachrichtigungen\n\n"

    msg += "/help - Zeigt eine Liste der anderen Befehle an, "
    msg += "mit denen du den Bot kontrollieren kannst.\n\n\n"

    msg += "Viel Erfolg beim Ticketkauf!\n\n"

    msg += "<i>Ein kleiner Tipp noch: Um zu erfahren, wie du ein reserviertes "
    msg += "Ticket dann kaufen kannst, lies dir das</i> /manual <i>durch.</i>\n\n\n"

    msg += "2018, Marius Montebaur"

    return msg


def help(_, chat_id):
    msg = "<b>Befehle 📢</b>\n\n"
    msg += "/help - Alle Befehle anzeigen\n"
    msg += "/manual - Anleitung zum Kauf der Tickets\n"
    msg += "/sub - Aktiviere Benachrichtigungen\n"
    msg += "/unsub - Dekativiere Benachrichtigungen\n"
    msg += "/link - Link zum Onlineshop von TixforGigs\n"
    msg += "/about - Infos über diesen Bot\n"

    return msg


def manual(_, chat_id):
    msg = "<b>Anleitung 📚</b>\n\n"
    msg += "Da du das Ticket nicht selber auf der Webseite von "
    msg += "TixforGigs in deinen Einkaufswagen schmeißt, sondern "
    msg += "dieser Bot das für dich übernimmt, funktioniert das Kaufen "
    msg += "des Tickets dann auch etwas anders, als normalerweise...\n\n"

    msg += "<i>Nicht hilfreich, weil diese Anleitung noch nicht fertig "
    msg += "ist. Einfach Monti fragen...</i>"

    return msg


def about(_, chat_id):
    msg = "<i>Über den</i> <b>splash Ticket Bot 😍</b>\n\n"
    msg += "Der Bot wurde in Python3 geschrieben und der ganze Code "
    msg += "kann auf GitHub eingesehen werden.\n\n"

    msg += "Da die Tickets fürs Splash dieses Jahr viel zu schnell "
    msg += "ausverkauft waren, habe ich diesen Bot programmiert, "
    msg += "der es allen meinen Freunden (die mit wollen) ermöglicht, "
    msg += "noch günstig und ohne viel Aufwand an Tickets zu kommen.\n\n"

    msg += "2018, Marius Montebaur"

    return msg


def sub(_, chat_id):
    xmlDb.add_user('waiting', chat_id)

    admin_msg = "Neuer Abonnent, <i>chat_id = " + chat_id + "</i>\n\n"
    admin_msg += "Bitte bestätigen oder ablehnen\n"
    admin_msg += "<code>/confirm</code>\n"
    admin_msg += "<code>/decline</code>"
    telegramMsg.notify_admins(admin_msg)

    msg = "Du bekommst eine Nachricht, sobald dein Abo vom "
    msg += "Admin bestätigt wurde."

    return msg


def unsub(_, chat_id):
    xmlDb.remove_user('users', chat_id)

    admin_msg = "Abo beendet, <i>chat_id = " + chat_id + "</i>"
    telegramMsg.notify_admins(admin_msg)

    msg = "Benachrichtigungen ausgeschaltet."

    return msg


def link(_, chat_id):
    msg = "<b>Link zum Ticketverkauf 🌍</b>\n"
    msg += '<a href="https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735">TixforGigs</a>'

    return msg


def system_info(_, chat_id):
    if not xmlDb.user_exists('admins', chat_id):
        return ""

    msg = "<b>System Info:</b>\n"
    for key in tB.bot_info:
        msg += key.replace('_', ' ') + ": " + tB.bot_info[key] + "\n"

    msg += "\nchat_id: " + chat_id
    return msg


def admin_confirm(msg, chat_id):
    if not xmlDb.user_exists('admins', chat_id):
        return ""

    client_chat_id = msg
    # msg enthaelt die chat_id des Users, der hinzugefuegt werden soll
    if not xmlDb.user_exists('waiting', client_chat_id):
        error_msg = "User nicht in der waiting-Liste.\n"
        error_msg += "<i>chat_id = " + client_chat_id + "</i>"
        return error_msg

    xmlDb.remove_user('waiting', client_chat_id)
    xmlDb.add_user('users', client_chat_id)

    client_msg = "🎉 Du erhälst jetzt Benachrichtigungen, sobald ein Ticket verfügbar ist."
    telegramMsg.notify_client(client_msg, client_chat_id)

    success_msg = "User erfolgreich angenommen.\n"
    success_msg += "<i>chat_id = " + client_chat_id + "</i>"
    return success_msg


def admin_decline(msg, chat_id):
    if not xmlDb.user_exists('admins', chat_id):
        return ""

    client_chat_id = msg
    # msg enthaelt die chat_id des Users, der hinzugefuegt werden soll
    if not xmlDb.user_exists('waiting', client_chat_id):
        return "User nicht in der waiting-Liste."

    xmlDb.remove_user('waiting', client_chat_id)
    xmlDb.add_user('blacklist', client_chat_id)

    client_msg = "Du wurdest abgelehnt."
    telegramMsg.notify_client(client_msg, client_chat_id)

    blacklist_msg = "User auf der Blacklist.\n"
    blacklist_msg += "<i>chat_id = " + client_chat_id + "</i>"
    return blacklist_msg


def test_formatting(msg, chat_id):
    return msg


def return_chat_id(msg, chat_id):
    return chat_id


def main():


    handler_dict = {'start': start,
                    'help': help,
                    'manual': manual,
                    'sub': sub,
                    'unsub': unsub,
                    'link': link,
                    'about': about,
                    'confirm': admin_confirm,
                    'decline': admin_decline,
                    'echo': test_formatting,
                    'chat_id': return_chat_id}

    telegramMsg.launch_cmd_handler(handler_dict)

    # sleep(8)

    # telegramMsg.notify_clients("<b>test</b>")
    # telegramMsg.notify_clients("test2")

    while True:
        sleep(1)


if __name__ == '__main__':
    main()

