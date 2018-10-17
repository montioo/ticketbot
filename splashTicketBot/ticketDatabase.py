import sqlite3
import time
import ticketBot as tB

db_name = "tix_stats.db"


def create_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("CREATE TABLE tickets (name text, price real, added integer, removed integer, i_reserved integer, version text)")

    conn.commit()
    conn.close()


def insert_dict(d):
    name = d['ticket_type']
    price = float(d['ticket_price'][:-1].replace(',', '.'))
    added = d['added']
    removed = d['removed']
    i_reserved = 1 if 'i_reserved' in d else 0
    insert_row(name, price, added, i_reserved, removed)


def insert_row(name, price, added, i_reserved, removed):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    entry = [name, price, int(added), int(removed), i_reserved, tB.bot_info['version']]
    c.execute("INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?)", entry)
    conn.commit()
    conn.close()


def print_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets")
    print(c.fetchall())
    conn.close()


def main():
    create_db()
    d = {   'ticket_type': 'Festivalticket Phase 1',
            'ticket_price': '144,50€',
            'added': time.time(),
            'removed': time.time()}
    # insert_dict(d)
    print_db()


if __name__ == "__main__":
    main()
