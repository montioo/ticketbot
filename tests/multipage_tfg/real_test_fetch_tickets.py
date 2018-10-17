

# erstes Programm, das mehrere Threads verwendet, um die Tickets aller
# verfuegbaren Seiten aufzulisten.

import requests
import threading
import time

from bs4 import BeautifulSoup as bs


# Fuer das Abfragen der einzelnen Seiten werden sowohl das Session-Objekt,
# als auch die Post-Daten der ersten Abfrage verwendet.
# Fuer die weiteren Abfragen (= Reservierungen) werden dann die aus
# den Antworten resultierenden post_data_dicts verwendet.



page_list_lock = threading.Lock()

url = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3"
}



def list_diff_stat(old, new):
    print("old:", old)
    print("new:", new)
    a_i = 0
    n_j = 0
    removed_list = []
    added_list = []
    while a_i < len(old) and n_j < len(new):
        print(old[a_i]['ticket_price'], "---", new[n_j]['ticket_price'])
        old_i_price = float(old[a_i]['ticket_price'][:-1].replace(',', '.'))
        new_j_price = float(new[n_j]['ticket_price'][:-1].replace(',', '.'))

        if old[a_i]['ticket_type'] == new[n_j]['ticket_type'] and old_i_price == new_j_price:
            # Preis und Name gleich -> Gleiches Ticket
            print(a_i, "---", n_j)
            a_i += 1
            n_j += 1
        elif old_i_price < new_j_price:
            # ein altes wurde entfernt
            print(a_i, "-----")
            removed_list.append(old[a_i])
            a_i += 1
        elif old_i_price > new_j_price:
            # neues wurde hinzugefuegt
            print("-----", n_j)
            added_list.append(new[n_j])
            n_j += 1
        else:
            # ticket_type unterschiedlich, aber preis gleich
            # sollte eigentlich nicht passieren
            print("WAAAS LOS:", a_i, n_j)
            print("old[a_i]:", old[a_i])
            print("new[n_j]:", new[n_j])
            a_i += 1
            n_j += 1


    print("a_i:", a_i, ", len(old):", len(old))
    print("n_j:", n_j, ", len(new):", len(new))
    for i in range(a_i, len(old)):
        print("i:", i)
        removed_list.append(old[a_i])

    for j in range(n_j, len(new)):
        print("j:", j)
        added_list.append(new[n_j])

    return removed_list, added_list



def print_cookies(c):
    print(cookies_to_string(c))


def cookies_to_string(c):
    if '.ASPXANONYMOUS' in c and 'ASP.NET_SessionId' in c:
        cookies = "\nCookies der Session:\n\n"
        cookies += "  .ASPXANONYMOUS:\n" + c['.ASPXANONYMOUS'] + "\n\n"
        cookies += "  ASP.NET_SessionId:\n" + c['ASP.NET_SessionId'] + "\n\n"
        return cookies
    return "Erforderliche Keys nicht im Dict"

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


def count_pages(tickets):
    complete_pages = tickets // 10
    partly_pages = 0 if tickets % 10 == 0 else 1
    return complete_pages + partly_pages


def get_ticketamount():
    # Session-Objekt behaelt die Cookies :D (nice)
    ses = requests.Session()

    page = ses.get(url, headers=header).content
    soup = bs(page, "lxml")

    ticket_amount_str = soup.find('span', class_='RESULTS_count').get_text().strip()
    ticket_amount = int(ticket_amount_str.split()[0])

    return ticket_amount, ses, soup


# Gibt die Liste mit Dicts schoen aus
def print_list_dict(ls):
    for d in ls:
        for key in d:
            print(" ", key, ":", d[key])
        print(" ")


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

        page_descriptor = "ctl00$MainContentPlaceHolder$DataPager2$ctl01$ctl{:02}".format(self.page-1)

        self.post_data["__EVENTTARGET"] = page_descriptor
        answ = self.ses.post(url, data=self.post_data, headers=header).content

        soup = bs(answ, "lxml")

        items_list_dict = available_tickets_from_soup(soup, self.page)
        new_post_data = get_post_datadict(soup)

        page_list_lock.acquire()
        self.results["tickets"][self.list_index] = items_list_dict
        self.results["post_data"][self.list_index] = new_post_data
        page_list_lock.release()

        print("Fertig mit Seite:", self.page)


def reserve_ticket(item, pDD):

    print("Try to reserve a ticket:")
    print("  name:", item['ticket_type'])
    print("  price:", item['ticket_price'])

    pDD["__EVENTTARGET"] = item['btn_name']
    ses = requests.Session()
    answ = ses.post(url, data=pDD, headers=header).content


    soup = bs(answ, "lxml")
    cart_items_new = int(soup.find(id='ctl00_shoppingCartControl__TotalItemsLabel').get_text())

    print("Versuchte Reservierung!")
    print("  " + item['ticket_type'] + ": " + item['ticket_price'] + "\n\n")
    print_cookies(ses.cookies)



def main():

    ticket_amount = 0
    ticket_list []

    new_ticket_amount, ses_p1, soup_p1 = get_ticketamount()

    if new_ticket_amount != ticket_amount:
        print_cookies(ses_p1.cookies)

        post_data_p1 = get_post_datadict(soup)
        tickets_p1 = available_tickets_from_soup(soup_p1)

        page_count = count_pages(ticket_amount)
        pages["tickets"] = [None] * page_count
        pages["post_data"] = [None] * page_count

        pages["tickets"][0] = tickets_p1
        pages["post_data"][0] = post_data_p1

        page_fetch_threads = []
        for page in range(2, page_count+1):
            page_thread = tickets_from_page(pages, page, ses_p1, post_data_p1)
            page_fetch_threads.append(page_thread)
            page_thread.start()


        for t in page_fetch_threads:
            t.join()


        # Liste aus Listen zusammensetzen (flattening the list)
        # "Flat is better than nested."
        new_flat_ticket_list = sum(pages["tickets"], [])

        removed_tix, new_tix = list_diff_stat(ticket_list, new_flat_ticket_list)

        print("-- REMOVED:")
        for r in removed_tix:
            print(r)

        print("-- ADDED:")
        for n in new_tix:
            print(n)
            

        ticket_list = new_flat_ticket_list
        ticket_amount = new_ticket_amount


        i = 1
        for p in pages:
            print("\n--- SEITE", i, "---")
            print_list_dict(p["tickets"])
            i += 1





    end = time.time()
    print("  ---> {0:.2f} Sekunden".format((end - start)))

    # Seite 2, Ticket 4
    reserve_ticket(pages[1]["tickets"][3], pages[1]["post_data"])


if __name__ == "__main__":
    main()
