import time


# Gibt die Liste mit Dicts schoen aus
def print_list_dict(ls):
    for d in ls:
        for key in d:
            print(key, ": ", d[key])
        print(" ")


def list_diff_stat(old, new):
    # print("-- OLD:")
    # print_list_dict(old)
    # print("-- NEW:")
    # print_list_dict(new)
    a_i = 0
    n_j = 0
    removed_list = []
    added_list = []
    complete_list = []
    while a_i < len(old) and n_j < len(new):
        print(old[a_i]['ticket_price'], "---", new[n_j]['ticket_price'])
        old_i_price = float(old[a_i]['ticket_price'][:-1].replace(',', '.'))
        new_j_price = float(new[n_j]['ticket_price'][:-1].replace(',', '.'))

        if old[a_i]['ticket_type'] == new[n_j]['ticket_type'] and old_i_price == new_j_price:
            # Preis und Name gleich -> Gleiches Ticket
            print(a_i, "---", n_j)
            complete_list.append(old[a_i])
            a_i += 1
            n_j += 1

        elif old_i_price < new_j_price:
            # ein altes wurde entfernt
            print(a_i, "-----")
            old[a_i]['removed'] = int(time.time())
            removed_list.append(old[a_i])
            a_i += 1

        elif old_i_price > new_j_price:
            # neues wurde hinzugefuegt
            print("-----", n_j)
            new[n_j]['added'] = int(time.time())
            added_list.append(new[n_j])
            complete_list.append(new[n_j])
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
        old[i]['removed'] = time.time()
        removed_list.append(old[i])

    for j in range(n_j, len(new)):
        print("j:", j)
        new[j]['added'] = time.time()
        added_list.append(new[j])
        complete_list.append(new[j])

    return removed_list, added_list, complete_list
