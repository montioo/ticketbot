import sqlite3

# db_name = "tix_stats.db"
db_name = "../../splashTicketBot/tix_stats.db"
version = "db_test"

def create_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("CREATE TABLE tickets (name text, price real, added integer, removed integer, version text)")

    conn.commit()
    conn.close()


def insert_dict(d):
    name = d['ticket_type']
    price = float(d['ticket_price'][:-1].replace(',', '.'))
    added = d['added']
    removed = d['removed']
    insert_row(name, price, added, removed)


def insert_row(name, price, added, removed):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    entry = [name, price, added, removed, version]
    c.execute("INSERT INTO tickets VALUES (?, ?, ?, ?, ?)", entry)
    conn.commit()
    conn.close()


def print_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets")
    print(c.fetchall())
    conn.close()


def main():
    # create_db()
    d = {   'ticket_type': 'Festivalticket Phase 1',
            'ticket_price': '144,50€',
            'added': 100,
            'removed': 400}
    # insert_dict(d)
    print_db()


if __name__ == "__main__":
    main()
