import requests
import threading
import time

from bs4 import BeautifulSoup as bs

url = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3"
}

def print_cookies(c):
    # if '.ASPXANONYMOUS' in c and 'ASP.NET_SessionId' in c:
    #     print("\n# Cookies der Session:\n# ")
    #     print("#   .ASPXANONYMOUS:     ", c['.ASPXANONYMOUS'], "\n#")
    #     print("#   ASP.NET_SessionId:  ", c['ASP.NET_SessionId'], "\n\n")
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


def fetch_session_postData():
    # Session-Objekt behaelt die Cookies :D (nice)
    ses = requests.Session()

    page = ses.get(url, headers=header).content
    soup = bs(page, "lxml")

    post_data = get_post_datadict(soup)

    return ses, post_data


# Gibt die Liste mit Dicts schoen aus
def print_list_dict(ls):
    for d in ls:
        for key in d:
            print(key, ": ", d[key])
        print(" ")


def available_tickets_from_soup(soup):
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

    return items_list_dict


def fetch_tickets_from_page(ses, post_data_dict, page):
    page_descriptor = "ctl00$MainContentPlaceHolder$DataPager2$ctl01$ctl{:02}".format(page-1)

    post_data_dict["__EVENTTARGET"] = page_descriptor
    answ = ses.post(url, data=post_data_dict, headers=header).content

    soup = bs(answ, "lxml")

    items_list_dict = available_tickets_from_soup(soup)
    # website_content = soup.find(id='layout_content').get_text()
    # print(website_content)

    # return items_list_dict

    new_post_data = get_post_datadict(soup)
    new_post_data['__EVENTTARGET'] = items_list_dict[0]['btn_name']
    # print(new_post_data)

    # Hier wird dann das Ticket der betreffenden Seite in den Einkaufswagen
    # gelegt.
    answ2 = ses.post(url, data=new_post_data, headers=header).content
    # print(answ2)
    print_cookies(ses.cookies)

    return items_list_dict


def main():
    start = time.time()

    ses, post_data_dict = fetch_session_postData()
    # Bei zu hohen Seitenzahlen antwortet der Server mit der ersten Seite
    page = 1
    items = fetch_tickets_from_page(ses, post_data_dict, page)
    print_list_dict(items)

    end = time.time()
    print("duration for:")
    print("- Session object fetch")
    print("- post back with request for specific page")
    print("- receiving and evaluating response")
    print("  ---> {0:.2f} Sekunden".format((end - start)))


if __name__ == "__main__":
    main()
