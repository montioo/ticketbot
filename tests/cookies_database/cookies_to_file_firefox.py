import sqlite3


# Speichert alle Cookeis, die im Speicher von Firefox sind,
# in einer Datei.
#
# Aufbau der Datenbank ist in dieser Datei hier erklaert


filename = 'cookies.sqlite'
db = sqlite3.connect(filename)
curs = db.cursor()

# Aufbau in der Tabelle sqlite_master beschrieben
curs.execute('SELECT * FROM sqlite_master')
print curs.fetchone()

# Aufbau:
# ('table', 'moz_cookies', 'moz_cookies', 2, "CREATE TABLE moz_cookies (id INTEGER PRIMARY KEY, baseDomain TEXT, originAttributes TEXT NOT NULL DEFAULT '', name TEXT, value TEXT, host TEXT, path TEXT, expiry INTEGER, lastAccessed INTEGER, creationTime INTEGER, isSecure INTEGER, isHttpOnly INTEGER, inBrowserElement INTEGER DEFAULT 0, sameSite INTEGER, CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes))")

curs.execute('SELECT * FROM moz_cookies')
print curs.fetchone()
# (id INTEGER PRIMARY KEY, baseDomain TEXT, originAttributes TEXT NOT NULL DEFAULT '', name TEXT, value TEXT, host TEXT, path TEXT, expiry INTEGER, lastAccessed INTEGER, creationTime INTEGER, isSecure INTEGER, isHttpOnly INTEGER, inBrowserElement INTEGER DEFAULT 0, sameSite INTEGER, CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes))
# Beispieltupel:
# (10302, 'tixforgigs.com', '', '.ASPXANONYMOUS', 'cJ3qkEvY0wEkAAAAZGIzNzg1MzUtMTA5My00MTg0LWIzMjQtZTJlZmI2Y2UxYzBitslbasv8l3Zlnh_z1m1a5k4cVYo1', 'www.tixforgigs.com', '/', 1524189718, 1518375236195963, 1518189723441276, 0, 1, 0, 0),

# interessante Felder:
#   baseDomain TEXT =>      'tixforgigs.com'
#   name TEXT =>            '.ASPXANONYMOUS'
#   value TEXT =>           'cJ3qkEvY0wEkAAAAZGIzNzg1MzUtMTA5My00MTg0LWIzMjQtZTJlZmI2Y2UxYzBitslbasv8l3Zlnh_z1m1a5k4cVYo1'
#   expiry INTEGER =>       1524189718
#   lastAccessed INTEGER => 1518375236195963 (10 erste Stellen sind Sekunden, 6 hintersten Nachkommaanteil)
#   creationTime INTEGER => 1518189723441276
#
# vorgehen:
#   suchen: baseDomain und name
#   aendern:    expiry (aktuell + 2 Monate oder so)
#               lastAccessed (aktuell*1.000.000, also Nachkommaanteil eliminieren)
#               creationTime (aktuell*1.000.000, also Nachkommaanteil eliminieren)

# Liste aus Tupeln in String verwandeln und in Datei schreiben
cookies_tuple_list = curs.fetchall()
cookies_str = ""
for tup in cookies_tuple_list:
    elem_str = ""
    for e in tup:
        elem_str += str(e) + ", "

    cookies_str += elem_str + "\n"

f = open('cookies_as_str.txt', 'w')

f.write(cookies_str)
f.close()
