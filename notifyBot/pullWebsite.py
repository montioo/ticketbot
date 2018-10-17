# http://docs.python-guide.org/en/latest/scenarios/scrape/

from lxml import html
import requests


class TicketEntry:
    title = ""
    price = ""

    def __init__(self, t, p):
        self.title = t
        self.price = p


def pullTixForGigs():

    addr = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'
    #addr = 'tfg_site/einTicket/TixForGigs.html'
    #addr = 'tfg_site/Ticket/TixForGigs.html'

    page = requests.get(addr)
    tree = html.fromstring(page.content)
    #print(page.text)
    placeholder = tree.xpath('//span[@id="ctl00_MainContentPlaceHolder__ticketResaleList_ctrl0_notavailableLabel"]/text()')

    if placeholder:
        if "leider keine Tickets" in placeholder[0]:
            return []

    available = []

    layout_content = tree.xpath('//div[@id="layout_content"]')

    resaleItemContainer = []

    for entry in layout_content[0].getchildren():
        #print(entry.attrib)
        attr_dict = entry.attrib
        if 'class' in attr_dict:
            if entry.attrib['class'] == "ResaleItemContainer clearfix":
                resaleItemContainer.append(entry)


    for c in resaleItemContainer:
        t = c[1].getchildren()[0].text_content().strip()
        p = c[2].getchildren()[0].text_content().strip()
        p = p.replace(' â¬', '€')
        p = p.replace('.', ',')
        available.append(TicketEntry(t, p))
        #print(t, p)

    if not available:
        available = "Ticketliste auf der Webseite"

    return available


def main():

    pullTixForGigs()


if __name__ == "__main__":
    main()
