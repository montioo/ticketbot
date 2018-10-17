import time
import datetime
import webTicket as webTix
import utility as util
import telegramMessenger as telegramMsg
import telegramHandler as telegramHndl
import polynomialInterpolation as polyInterp


# Autor: Marius Montebaur
#   Version: siehe unten
#   Kleine Fehlerbehebung bei Telegram Antwort auf undefinierten Befehl
# Datum: 10.04.18

# Debug output:
# https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python

# Error und StdOut in Datei: python3 ticketBot.py &> logs_test_feb-02_23-30.txt
# Mit Signal von ^C: kill -INT -17802
# Beispiel:
# $ python3 ticketBot.py &> logs_test_feb-02_23-47.txt &
# [1] 19780
# kill -INT -19780  # !!! Wichtig, um Logdatei zu behalten

# Alle Keys und Values muessen Strings sein
bot_info = {
    'version': "2.5.5",
    'start_time': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
}


def time_to_float(hours, minutes):
    m = minutes/60
    return hours + m


def main():
    print("    ticketBot, start:", util.get_time_string())
    print("             version:", bot_info['version'])

    handler_dict = {'start': telegramHndl.start,
                    'help': telegramHndl.help,
                    'manual': telegramHndl.manual,
                    'sub': telegramHndl.sub,
                    'unsub': telegramHndl.unsub,
                    'link': telegramHndl.link,
                    'about': telegramHndl.about,
                    'systeminfo': telegramHndl.system_info,
                    'confirm': telegramHndl.admin_confirm,
                    'decline': telegramHndl.admin_decline}

    telegramMsg.launch_cmd_handler(handler_dict)

    points = [(0.5, 4), (1, 8), (9, 8), (10, 4), (17, 4), (18, 6), (21, 6), (22, 4)]
    timer_interpol = polyInterp.InterpolatedFunction(points, 24, 3)

    start_time = time.time()
    intervall = 100

    i = 0

    ticket_list, _ = webTix.fetch_all_tickets(0)
    for ticket in ticket_list:
        ticket['added'] = 0

    while True:
        zeit = datetime.datetime.now()
        zeit_float = time_to_float(zeit.hour, zeit.minute)
        zeit_sleep = timer_interpol.value(zeit_float)
        time.sleep(zeit_sleep)

        ticket_list = webTix.list_tix_diff(ticket_list)

        i += 1
        if i == intervall:
            dauer = time.time() - start_time
            dauer_str = str(dauer)[:5]
            time_str = util.get_time_string()
            print(time_str + ":,", str(intervall), "Anfragen in", dauer_str, "Sek gesendet.")
            i = 0
            start_time = time.time()


if __name__ == "__main__":
    main()
