#!/bin/bash

cd /srv/HistoryDB-Web
git pull
python3 create_new_key.py

cd historydb
python3 manage.py makemigrations
python3 manage.py migrate

touch docker_entrypoint
