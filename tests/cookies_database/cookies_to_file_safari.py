
# Darstellung der Datenbank von Safari. Datei von: ~/Library/Safari/Databases/Databases.db
# Die Datei war auch nur 20MB gross, also muss da irgendwo noch was anderes sein. Hoffentlich
# aber nicht auf mehrere Dateien verteilt... Da ist Firefox sympathischer.
#
# >>> import sqlite3
# >>> db = sqlite3.connect('safari_cookies.db')
# >>> curs = db.cursor()
# >>> curs.execute('SELECT * FROM sqlite_master')
# <sqlite3.Cursor object at 0x10d454880>
# >>> print(curs.fetchone())
# ('table', 'Origins', 'Origins', 2, 'CREATE TABLE Origins (origin TEXT UNIQUE ON CONFLICT REPLACE, quota INTEGER NOT NULL ON CONFLICT FAIL)')
#
# >>> curs.execute('SELECT * FROM Origins')
# <sqlite3.Cursor object at 0x10d454880>
# >>> print(curs.fetchall())
# [('https_www.fossil.com_0', 5000000), ('https_www.bitcoin.de_0', 5000000), ('https_tu-berlin.hosted.exlibrisgroup.com_0', 5000000)]
# >>>
