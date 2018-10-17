import requests

from bs4 import BeautifulSoup as bs



url = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3"
}

# ses = requests.Session()


'''
Um die Tickets von verschiedenen Seiten ueberblicken und verwalten zu koennen,
brauche ich eine vernuenftige Datenstruktur, die das leistet.
Eingabe sollen die Tickets einer Seite sein. Die Datenstruktur soll dann
selbststaendig schauen ob und WAS sich gaendert hat.
Wenn ein neues Ticket kam, muessen die Tickets 'aufgeschoben' werden.
Wenn eins verschwunden ist, muessen Tickets von hoeheren Seiten
nachruecken.
Dabei koennen regelmaessig neue Seiten hinzukommen oder entfernt werden.

Die Reservierung neuer Tickets soll dann auch von dieser Datenstruktur /
Verwaltungseinheit geregelt werden.

Zusaetzlich soll dann noch eine Art Datenbank erstellt werden
(sqlite vielleicht), die Tickets und ihre Onlinezeit speichert. Also:
Ticketart, Preis, Zeit des Erscheinens, Verschwindens und Zeit, nachdem das
Ticket reserviert wurde. Wobei nur die Reservierung interessant ist, die das
Ticket dann auch von der Seite entfernt hat.

Damit sollen dann tolle Graphen gezeichnet werden koennen.

Hinterliegende SQLite Datenbank, die dann von dem Server mit Updates bezueglich
Tickets und ihren 'Zeiten' beschrieben werden kann. Ausserdem koennen die Daten
auf Anfrage gelesen, geplottet und per Telegram versendet werden :D
Man ist das nice!

Sehr suess uebrigens: https://www.sqlite.org/whentouse.html
-> Immer nur ein Schreibzugriff gleichzeitig
'''


def page_count(tickets):
    complete_pages = tickets // 10
    partly_pages = 0 if tickets % 10 == 0 else 1
    return complete_pages + partly_pages


def get_ticketamount():
    page = requests.get(url, headers=header).content
    soup = bs(page, 'lxml')

    results_str = soup.find('span', class_='RESULTS_count').get_text().strip()
    results = int(results_str.split()[0])

    print("Seiten:", page_count(results))
    return results



def main():
    print("Tickets:", get_ticketamount())


if __name__ == "__main__":
    main()
