from bs4 import BeautifulSoup
import requests


# Vielleicht:
# https://blog.scrapinghub.com/2016/04/20/scrapy-tips-from-the-pros-april-2016-edition/

# aehnlich aber ohne scheiss session-coockies
# https://scraperwiki.com/2011/11/how-to-get-along-with-an-asp-webpage/

data = {
    'ctl00__scriptManager_HiddenField':'',
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE' : '',
    '__VIEWSTATEGENERATOR' : '',
    '__SCROLLPOSITIONX':'0',
    '__SCROLLPOSITIONY':'160',
    '__VIEWSTATEENCRYPTED':'',
    '__PREVIOUSPAGE' : '',
    '__EVENTVALIDATION' : ''
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3"
}

url = 'https://www.tixforgigs.com/site/Pages/Shop/TicketResales.aspx?ID=21735'

# Session-Objekt behaelt die Cookies :D
with requests.Session() as s:
    page = s.get(url, headers=headers).content
    soup = BeautifulSoup(page, "lxml")
    data["__VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
    data["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
    data["__PREVIOUSPAGE"] = soup.select_one("#__PREVIOUSPAGE")["value"]
    data["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]
    data["__EVENTTARGET"] = 'ctl00$MainContentPlaceHolder$_ticketResaleList$ctrl8$_addToCartCommand'

    print(s.cookies)
    s.post(url, data=data, headers=headers)
    open_page = s.get(url, headers=headers).content

    print(s.cookies)
    #Check content
    soup_2 = BeautifulSoup(open_page, "lxml")
    cart_items_amount = soup_2.find_all(id='ctl00_shoppingCartControl__TotalItemsLabel')
    print(cart_items_amount)
