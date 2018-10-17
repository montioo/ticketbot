import requests
import threading
import time
import datetime

from bs4 import BeautifulSoup as bs

import telegramMessenger as telegramMsg

import utility as util
import tixStatistics as stats
import ticketDatabase as tixDb


# erstes Programm, das mehrere Threads verwendet, um die Tickets aller
# verfuegbaren Seiten aufzulisten.


page_list_lock = threading.Lock()


# Dict fuer Post-Anfrage mit benoetigten Werten erstellen
def get_post_datadict(soup):

    data = {"__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": soup.select_one("#__VIEWSTATE")["value"],
            "__VIEWSTATEGENERATOR": soup.select_one("#__VIEWSTATEGENERATOR")["value"],
            "__VIEWSTATEENCRYPTED": "",
            "__PREVIOUSPAGE": soup.select_one("#__PREVIOUSPAGE")["value"],
            "__EVENTVALIDATION": soup.select_one("#__EVENTVALIDATION")["value"]}

    return data


# Erstellt eine Liste mit Dictionaries. Jedes Dict enthaelt Infos zu einem
# angebotenen Ticket
def fetch_tickets():
    # Session-Objekt behaelt die Cookies :D (nice)
    ses = requests.Session()

    page = ses.get(util.url, headers=util.header).content
    soup = bs(page, "lxml")

    # ResaleItemContainer enthalet Infos zu jeweils einem Ticket
    items = soup.find_all('div', class_='ResaleItemContainer clearfix')

    items_list_dict = []

    for i in items:
        container_dict = {}
        container_content = i.find_all('div', class_='ItemElement')

        container_dict['ticket_type'] = container_content[1].get_text().strip()
        container_dict['ticket_price'] = container_content[2].get_text().strip()

        # Finde input-Element und nimm den Wert des name-Attributs
        container_dict['btn_name'] = container_content[6].find('input')['name']
        container_dict['still_available'] = ('addToCartCommand' in container_dict['btn_name'])

        items_list_dict.append(container_dict)

    post_data = get_post_datadict(soup)

    cart_items_amount = int(soup.find(id='ctl00_shoppingCartControl__TotalItemsLabel').get_text())

    return ses, items_list_dict, post_data, cart_items_amount


def try_reserve_ticket(item, post_datadict):
    reserver = ReserveTicket(item, post_datadict)
    reserver.start()


class ReserveTicket(threading.Thread):
    def __init__(self, item, post_data_dict):
        threading.Thread.__init__(self)
        self.item = item
        self.pDD = post_data_dict

    def run(self):
        start = time.time()
        print("Try to reserve a ticket:")
        print("  name:", self.item['ticket_type'])
        print("  price:", self.item['ticket_price'])

        self.pDD["__EVENTTARGET"] = self.item['btn_name']
        ses = requests.Session()
        answ = ses.post(util.url, data=self.pDD, headers=util.header).content
        util.print_cookies(ses.cookies)
        end = time.time()
        print("  duration (1x post):", (end - start))

        self.item['i_reserved'] = True

        soup = bs(answ, "lxml")
        cart_items = int(soup.find(id='ctl00_shoppingCartControl__TotalItemsLabel').get_text())

        if cart_items != 0:
            msg = "Neues Ticket reserviert!\n"
            msg += "  " + self.item['ticket_type'] + ": " + self.item['ticket_price'] + "\n\n"
            msg += util.cookies_to_string(ses.cookies)
            telegramMsg.notify_clients(msg)
        else:
            msg = "Ich war zu langsam... :-("
            msg += "  " + self.item['ticket_type'] + ": " + self.item['ticket_price'] + "\n\n"
            msg += util.cookies_to_string(ses.cookies)
            telegramMsg.notify_admins(msg)


def reserve_new_ticket(item, pDD):
    print("Try to reserve a ticket:")
    print("  name:", item['ticket_type'])
    print("  price:", item['ticket_price'])

    pDD["__EVENTTARGET"] = item['btn_name']
    ses = requests.Session()
    answ = ses.post(util.url, data=pDD, headers=util.header).content

    soup = bs(answ, "lxml")
    cart_items_new = int(soup.find(id='ctl00_shoppingCartControl__TotalItemsLabel').get_text())

    print("Versuchte Reservierung!")
    print("  " + item['ticket_type'] + ": " + item['ticket_price'] + "\n\n")
    util.print_cookies(ses.cookies)


def count_pages(tickets):
    complete_pages = tickets // 10
    partly_pages = 0 if tickets % 10 == 0 else 1
    return complete_pages + partly_pages


def count_tickets():
    # Session-Objekt behaelt die Cookies :D (nice)
    ses = requests.Session()

    page = ses.get(util.url, headers=util.header).content
    soup = bs(page, "lxml")

    ticket_amount_str = soup.find('span', class_='RESULTS_count').get_text().strip()
    ticket_amount = int(ticket_amount_str.split()[0])

    return ticket_amount, ses, soup


def available_tickets_from_soup(soup, page):
    # ResaleItemContainer enthalet Infos zu jeweils einem Ticket
    items = soup.find_all('div', class_='ResaleItemContainer clearfix')

    items_list_dict = []

    for i in items:
        container_dict = {}
        container_content = i.find_all('div', class_='ItemElement')

        container_dict['ticket_type'] = container_content[1].get_text().strip()
        container_dict['ticket_price'] = container_content[2].get_text().strip()

        # Finde input-Element und nimm den Wert des name-Attributs
        container_dict['btn_name'] = container_content[6].find('input')['name']
        container_dict['still_available'] = ('addToCartCommand' in container_dict['btn_name'])

        container_dict['page'] = page

        items_list_dict.append(container_dict)

    return items_list_dict


# Fuer das Abfragen der einzelnen Seiten werden sowohl das Session-Objekt,
# als auch die Post-Daten der ersten Abfrage verwendet.
# Fuer die weiteren Abfragen (= Reservierungen) werden dann die aus
# den Antworten resultierenden post_data_dicts verwendet.
class tickets_from_page(threading.Thread):
    def __init__(self, result_list, page, ses, post_data):
        threading.Thread.__init__(self)
        # Dict mit Listen, in die die Daten einer Seite einsortiert werden sollen
        self.results = result_list
        # Index in der Liste
        self.list_index = page - 1
        # Seite, die abgefragt werden soll
        self.page = page
        # Session-Objekt, das für die erste Anfrage verwendet wurde
        self.ses = ses
        # Post daten, die in der Antwort der ersten Anfrage standen
        self.post_data = post_data

    def run(self):
        print("Starte mit Seite:", self.page)

        page_descriptor = "ctl00$MainContentPlaceHolder$DataPager2$ctl01$ctl{:02}".format(self.page - 1)

        self.post_data["__EVENTTARGET"] = page_descriptor
        answ = self.ses.post(util.url, data=self.post_data, headers=util.header).content

        soup = bs(answ, "lxml")

        items_list_dict = available_tickets_from_soup(soup, self.page)
        new_post_data = get_post_datadict(soup)

        page_list_lock.acquire()
        self.results["tickets"][self.list_index] = items_list_dict
        self.results["post_data"][self.list_index] = new_post_data
        page_list_lock.release()

        print("Fertig mit Seite:", self.page)


# Laedt all auf der Webseite aufgefuehrten Tickets, wenn sich die Anzahl der Tickets
# geaendert hat.
def fetch_all_tickets(ticket_amount):

    new_ticket_amount, ses_p1, soup_p1 = count_tickets()

    if new_ticket_amount != ticket_amount and new_ticket_amount > 0:

        # msg = "Aenderung des Angebots"
        # telegramMsg.notify_admins(msg)

        print("AENDERUNG DES ANGEBOTS:")
        print(util.get_time_string())

        post_data_p1 = get_post_datadict(soup_p1)
        tickets_p1 = available_tickets_from_soup(soup_p1, 1)

        page_count = count_pages(new_ticket_amount)

        pages = {
            "tickets": [None] * page_count,
            "post_data": [None] * page_count
        }

        pages["tickets"][0] = tickets_p1
        pages["post_data"][0] = post_data_p1

        page_fetch_threads = []
        for page in range(2, page_count + 1):
            page_thread = tickets_from_page(pages, page, ses_p1, post_data_p1)
            page_fetch_threads.append(page_thread)
            page_thread.start()

        for t in page_fetch_threads:
            t.join()

        # Liste aus Listen zusammensetzen (flattening the list)
        # "Flat is better than nested."
        # enthaelt alle Tickets jeweils mit key 'page'
        new_flat_ticket_list = sum(pages["tickets"], [])
        # enthalet die post_data_dicts der einzelnen Seiten um ein Ticket
        # zu reservieren.
        page_post_data = pages["post_data"]

        return new_flat_ticket_list, page_post_data

    return None, None


# old_ticket_list: Tickets bei der letzten Abfrage
# curr_ticket_list: Tickets die aktuell auf der Seite sind, aber ohne Zeitstempel
# complete_ticket_list: aktuelle Tickets, mit Zeitstempeln uebernommen von den alten Tickets
def list_tix_diff(old_ticket_list):

    curr_ticket_list, page_post_data = fetch_all_tickets(len(old_ticket_list))

    if curr_ticket_list and page_post_data:

        removed_tix, new_tix, complete_ticket_list = stats.list_diff_stat(old_ticket_list, curr_ticket_list)

        print("-- REMOVED:")
        for r in removed_tix:
            tixDb.insert_dict(r)
            msg = "Ticket entfernt:\n"
            msg += "  " + r['ticket_type'] + ": " + r['ticket_price'] + "\n"
            msg += "  Seite: " + str(r['page']) + "\n"
            added_time = datetime.datetime.fromtimestamp(r['added']).strftime('%d.%m.%Y %H:%M:%S')
            removed_time = datetime.datetime.fromtimestamp(r['removed']).strftime('%d.%m.%Y %H:%M:%S')
            msg += "  hinzugefügt: " + added_time + "\n"
            msg += "  entfernt: " + removed_time + "\n"
            telegramMsg.notify_admins(msg)
            print(r)

        print("-- ADDED:")
        for n in new_tix:
            if float(n['ticket_price'][:-1].replace(',', '.')) < 155.0 and "Phase" in n['ticket_type']:
                # Normales Festivalticket und Preis kleiner als 155 => also reservieren
                pdd_for_page = page_post_data[n["page"] - 1]
                try_reserve_ticket(n, pdd_for_page)
            else:
                msg = "Neues Ticket (nicht reserviert):\n"
                msg += "  " + n['ticket_type'] + ": " + n['ticket_price'] + "\n"
                msg += "  Seite: " + str(n['page']) + "\n"
                telegramMsg.notify_admins(msg)
            print(n)

        print("\n\n\n--- ENDE AENDERUNG ---\n\n\n")

        return complete_ticket_list

    return old_ticket_list


def main():
    pass


if __name__ == "__main__":
    main()
