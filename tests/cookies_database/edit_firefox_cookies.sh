#!/bin/bash

cp ~/Library/Application\ Support/Firefox/Profiles/7alym8v6.default/cookies.sqlite ~/Desktop/

# Vorheriges Backup nicht ueberschreiben
cp -n ~/Desktop/cookies.sqlite ~/Desktop/.firefox_cookies_backup.sqlite

python firefox_cookies_sqlite.py ~/Desktop/cookies.sqlite

cp ~/Desktop/cookies.sqlite ~/Library/Application\ Support/Firefox/Profiles/7alym8v6.default/cookies.sqlite

# Ueberbleibsel der sqlite Datenbankbearbeitung
rm ~/Desktop/cookies.sqlite
rm ~/Desktop/cookies.sqlite-shm
rm ~/Desktop/cookies.sqlite-wal

echo "Cookies erfolgreich bearbeitet"
