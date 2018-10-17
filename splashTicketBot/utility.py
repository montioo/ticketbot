from datetime import datetime


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3"
}

url = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'


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


# Elemente von first minus Elemente von second
# ctrlxx ist keine Hilfe, da Tickets nach Preis sortiert werden
# name="ctl00$MainContentPlaceHolder$_ticketResaleList$ctrl8$_addToCartCommand"
# name="ctl00$MainContentPlaceHolder$_ticketResaleList$ctrl2$_shoppingCartNotAvailableImage"
# Elemente gleich, wenn
# - Name und Preis gleich
#
# Elemente von neu, die auch schon in alt waren
# Listen, sortiert nach price
# wenn name und price gleich, ist es gleiches Element
#   (unabhaengig von Einkaufswagenstatus)
# geht einfach mal davon aus, dass wenn neue Tickets kommen,
# sie unter bestehenden mit dem gleichen Preis einsortiert werden
#
# siehe Foto im documentation Ordner fuer grafische Darstellung
def list_diff(neu, alt):
    diff = []
    # ai = 0  # alt_index
    ni = 0  # neu_index
    # alen = len(alt)

    for ai in range(len(alt)):
        while not (alt[ai]['ticket_type'] == neu[ni]['ticket_type'] and alt[ai]['ticket_price'] == neu[ni]['ticket_price']):
            diff.append(neu[ni])
            ni += 1
            if ni == len(neu):
                break
        ni += 1

    if ni < len(neu):
        for i in range(ni, len(neu)):
            diff.append(neu[i])

    return diff


# https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
def get_time_string():
    t = datetime.now()
    pretty_t = t.strftime('%a. %d. %b. %Y, %H:%M:%S')
    return pretty_t


def main():
    # list_diff-Testcase
    alt = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl4'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl6'}]

    neu = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '14,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl4'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl6'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl8'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl10'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl12'}
    ]

    diff = list_diff(neu, alt)

    print(diff)


if __name__ == "__main__":
    main()