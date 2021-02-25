#!/bin/bash

cd /srv/HistoryDB-Web
git pull
python3 web-reset.py

cd historydb
python3 manage.py makemigrations
python3 manage.py migrate

touch web_entrypoint
