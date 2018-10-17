import threading

listLock = threading.Lock()

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

'''
def list_diff(neu, alt):
    diff = []
    ni = 0  # neu_index

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
'''


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


class dummyPullThread(threading.Thread):
    def __init__(self, result_list, list_elem, to_add):
        threading.Thread.__init__(self)
        self.result_list = result_list
        self.list_elem = list_elem
        # wird natuerlich in der Praxis aus der Webseite extrahiert
        self.output_list = to_add

    def run(self):
        print("Starte:", self.list_elem)
        listLock.acquire()
        self.result_list[self.list_elem] = self.output_list
        listLock.release()
        print("Fertig", self.list_elem)


def test_add():

    # list_diff-Testcase
    alt_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl4'}]

    alt_p2 = [
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl0'}]

    neu_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '14,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl4'}]

    neu_p2 = [
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl4'}]

    neu_p3 = [
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl0'}]

    alte_liste = alt_p1 + alt_p2

    page_count = 3
    neue_liste = [None] * page_count

    # Liste mit mehreren Threads zusammensetzen

    page1_tix_thread = dummyPullThread(neue_liste, 0, neu_p1)
    page2_tix_thread = dummyPullThread(neue_liste, 1, neu_p2)
    page3_tix_thread = dummyPullThread(neue_liste, 2, neu_p3)

    page1_tix_thread.start()
    page2_tix_thread.start()
    page3_tix_thread.start()

    page1_tix_thread.join()
    page2_tix_thread.join()
    page3_tix_thread.join()

    print("new_list")
    print(neue_liste)

    # Liste aus Listen zusammensetzen (flattening the list)
    # "Flat is better than nested."
    flat_list = sum(neue_liste, [])

    # Listen vergleichen

    rem, add = list_diff_stat(alte_liste, flat_list)
    print("removed:")
    print(rem)
    print("added:")
    print(add)


def test_remove():

    # list_diff-Testcase
    alt_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl4'}]

    alt_p2 = [
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl0'}]

    neu_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '14,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl4'}]

    neu_p2 = [
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl4'}]

    neu_p3 = [
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl0'}]

    alte_liste = neu_p1 + neu_p2 + neu_p3

    page_count = 2
    neue_liste = [None] * page_count

    # Liste mit mehreren Threads zusammensetzen

    page1_tix_thread = dummyPullThread(neue_liste, 0, alt_p1)
    page2_tix_thread = dummyPullThread(neue_liste, 1, alt_p2)

    page1_tix_thread.start()
    page2_tix_thread.start()

    page1_tix_thread.join()
    page2_tix_thread.join()

    print("new_list")
    print(neue_liste)

    # Liste aus Listen zusammensetzen (flattening the list)
    # "Flat is better than nested."
    flat_list = sum(neue_liste, [])

    # Listen vergleichen

    rem, add = list_diff_stat(alte_liste, flat_list)
    print("removed:")
    print(rem)
    print("added:")
    print(add)



def test_add_remove():

    # list_diff-Testcase
    alt_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl4'}]

    alt_p2 = [
        {'ticket_type': 'Festivalticket Phase 1',
         'ticket_price': '144,50€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl2'}]

    neu_p1 = [
        {'ticket_type': 'Parkticket',
         'ticket_price': '14,00€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Parkticket',
         'ticket_price': '15,00€',
         'btn_name': 'ctrl4'}]

    neu_p2 = [
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl0'},
        {'ticket_type': 'Camping Plus',
         'ticket_price': '50,60€',
         'btn_name': 'ctrl2'},
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl4'}]

    neu_p3 = [
        {'ticket_type': 'Festivalticket Phase 3',
         'ticket_price': '178,90€',
         'btn_name': 'ctrl0'}]

    alte_liste = alt_p1 + alt_p2

    page_count = 3
    neue_liste = [None] * page_count

    # Liste mit mehreren Threads zusammensetzen

    page1_tix_thread = dummyPullThread(neue_liste, 0, neu_p1)
    page2_tix_thread = dummyPullThread(neue_liste, 1, neu_p2)
    page3_tix_thread = dummyPullThread(neue_liste, 2, neu_p3)

    page1_tix_thread.start()
    page2_tix_thread.start()
    page3_tix_thread.start()

    page1_tix_thread.join()
    page2_tix_thread.join()
    page3_tix_thread.join()

    print("new_list")
    print(neue_liste)

    # Liste aus Listen zusammensetzen (flattening the list)
    # "Flat is better than nested."
    flat_list = sum(neue_liste, [])

    # Listen vergleichen

    rem, add = list_diff_stat(alte_liste, flat_list)
    print("removed:")
    print(rem)
    print("added:")
    print(add)


def main():
    test_add()
    print("----------------")
    test_remove()
    print("----------------")
    test_add_remove()

    print("Sieht gut aus :-)")


if __name__ == "__main__":
    main()
