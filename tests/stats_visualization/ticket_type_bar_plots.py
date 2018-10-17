import sqlite3
import collections
import matplotlib.pyplot as plt



def import_db():
    conn = sqlite3.connect('tix_stats.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets')
    tickets = []
    for e in c.fetchall():
        # <class 'tuple'>
        # ('Festivalticket Phase 3', 181.5, 1522757267, 1522759645, 0, '2.5.4')
        t = {
            'type': e[0],
            'price': e[1],
            'added': e[2],
            'removed': e[3],
            'i_reserved': e[4],
            'version': e[5]
        }
        tickets.append(t)
    conn.close()
    return tickets


# def main():
tickets = import_db()

count = collections.Counter()
for t in tickets:
    count[t['type']] += 1

labels, values = zip(*count.items())

indexes = range(len(labels))

width = 1

plt.bar(indexes, values, width)
plt.xticks(indexes, labels)
plt.show()

#plt.bar(count)
#plt.show()


# if __name__ == "__main__":
#     main()
