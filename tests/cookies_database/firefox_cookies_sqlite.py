import sqlite3
import time
import sys

# Bearbeitet die Cookies-Datenbank von Firefox
# Werte von Telegram-Nachrich einsetzen
#
# ACHTUNG:
#   Nur ausfuehren, wenn es von der Datenbank ein Backup gibt

# Zugriffsrechte in einem Verzeichnis:
#   ! python muss in dem Verzeichnis lesen und schreiben duerfen
#   Workaround -> Shell-Script kopiert sqlite-Datenbank auf Desktop

# Cookies Savelocation (Beide sind sqlite-Datenbank)
#   Firefox: ~/Library/Application\ Support/Firefox/Profiles/7alym8v6.default/cookies.sqlite
#   Safari: ~/Library/Safari/Databases/Databases.db


def get_entry(curs, arg_dict={'baseDomain': 'tixforgigs.com', 'name': '.ASPXANONYMOUS'}, print_entry=True):
    # Anfragen an Tabelle stellen
    # https://docs.python.org/2/library/sqlite3.html

    # domain_name = 'tixforgigs.com'
    # cookie_name = '.ASPXANONYMOUS'
    args = (arg_dict['baseDomain'], arg_dict['name'])
    curs.execute('SELECT * FROM moz_cookies WHERE baseDomain=? AND name=?', args)
    # .fetchall() -> liefert Liste von Tupeln
    # .fetchone() -> liefert Tupel
    entry = curs.fetchone()
    if print_entry:
        print entry
        print ""

    return entry


def print_entrys(curs, arg_dict={'baseDomain': 'tixforgigs.com'}):
    curs.execute('SELECT * FROM moz_cookies WHERE baseDomain=?', (arg_dict['baseDomain'],))
    # .fetchall() -> liefert Liste von Tupeln
    # .fetchone() -> liefert Tupel
    print "Print all entrys for baseDomain =", arg_dict['baseDomain']
    print curs.fetchall()
    print ""


def change_cookies(curs, upd):
    # INSERT INTO: http://www.sqlitetutorial.net/sqlite-insert/

    entry = get_entry(curs, upd, False)

    if entry:
        # Eintrag vorhanden und muss aktualisiert werden
        cmd = "UPDATE moz_cookies SET value=?, expiry=?, lastAccessed=?, creationTime=? WHERE baseDomain=? AND name=?"
        values = (upd['value'], upd['expiry'], upd['lastAccessed'], upd['creationTime'], upd['baseDomain'], upd['name'])
        curs.execute(cmd, values)
    else:
        # Eintrag muss erst erstellt werden
        cmd = "INSERT INTO moz_cookies (baseDomain, originAttributes, name, value, host, path, expiry, lastAccessed, creationTime, isSecure, isHttpOnly, inBrowserElement, sameSite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (upd['baseDomain'], upd['originAttributes'], upd['name'], upd['value'], upd['host'], upd['path'])
        values += (upd['expiry'], upd['lastAccessed'], upd['creationTime'], upd['isSecure'])
        values += (upd['isHttpOnly'], upd['inBrowserElement'], upd['sameSite'])
        curs.execute(cmd, values)

    print "After UPDATE / INSERT INTO"
    get_entry(curs, upd, print_entry=True)


def delete_cookies(curs, keep_names=[]):
    # DELETE: http://www.sqlitetutorial.net/sqlite-delete/
    value_tuple = ('tixforgigs.com',)

    keep_string = ""
    for e in keep_names:
        keep_string += " AND name!=?"
        value_tuple += (e,)

    cmd = "DELETE FROM moz_cookies WHERE baseDomain=?" + keep_string
    curs.execute(cmd, value_tuple)


def get_cookies_dict():
    # (id INTEGER PRIMARY KEY, baseDomain TEXT, originAttributes TEXT NOT NULL DEFAULT '', name TEXT, value TEXT, host TEXT, path TEXT, expiry INTEGER, lastAccessed INTEGER, creationTime INTEGER, isSecure INTEGER, isHttpOnly INTEGER, inBrowserElement INTEGER DEFAULT 0, sameSite INTEGER, CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes))
    # Beispieltupel:
    # (10302, 'tixforgigs.com', '', '.ASPXANONYMOUS', 'cJ3qkEvY0wEkAAAAZGIzNzg1MzUtMTA5My00MTg0LWIzMjQtZTJlZmI2Y2UxYzBitslbasv8l3Zlnh_z1m1a5k4cVYo1', 'www.tixforgigs.com', '/', 1524189718, 1518375236195963, 1518189723441276, 0, 1, 0, 0),

    upd = {}  # Update fuer die Datenbank
    upd['baseDomain'] = 'tixforgigs.com'
    upd['originAttributes'] = ''
    upd['name'] = 'COOKIE_NAME'  # .ASPXANONYMOUS
    upd['value'] = 'COOKIE_VALUE'  # muss noch gesetzt werden
    upd['host'] = 'www.tixforgigs.com'
    upd['path'] = '/'
    upd['expiry'] = int(time.time()) + 5184000 #aktuell + Sekunden in 2 Monaten
    upd['lastAccessed'] = int(time.time() * 1000000)
    upd['creationTime'] = int(time.time() * 1000000)
    upd['isSecure'] = 0
    upd['isHttpOnly'] = 1
    upd['inBrowserElement'] = 0
    upd['sameSite'] = 0
    return upd


def main():
    if len(sys.argv) == 1:
        print "\nBitte den Pfad zur .sqlite-Datei als Argument uebergeben!"
        print "  Beispiel: python3 sqlite_cookies.py ~/Desktop/cookies.sqlite\n"
        return -1

    filename = sys.argv[1]
    db = sqlite3.connect(filename)
    curs = db.cursor()

    print_entrys(curs)
    # get_entry(curs, upd, print_entry=True)

    delete_cookies(curs, ['.ASPXANONYMOUS', 'ASP.NET_SessionId'])

    upd = get_cookies_dict()

    upd['name'] = '.ASPXANONYMOUS'
    upd['value'] = 'wOhow17i0wEkAAAAM2ZjNDFiNzQtM2UyZS00NzE0LWFmMzAtYTIzZmY2ZmMyZTFipvrAXaQJi6RANu-uHumdWMcXHlc1'
    change_cookies(curs, upd)

    upd['name'] = 'ASP.NET_SessionId'
    upd['value'] = 'qseragnyvwxjyzbzvq0b1yli'
    change_cookies(curs, upd)


    print_entrys(curs)

    db.commit()  # Aenderungen speichern
    db.close()  # Verbindung schliessen

    return 0


if __name__ == "__main__":
    main()
