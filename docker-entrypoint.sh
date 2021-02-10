#!/bin/bash

mkdir -p $HISTORYDB_STORAGE/sqlite_data
export HISTORYDB_SQLITE_DATA=$HISTORYDB_STORAGE/sqlite_data
mkdir -p $HISTORYDB_STORAGE/mongodb_data
export HISTORYDB_MONGODB_DATA=$HISTORYDB_STORAGE/mongodb_data

cd /srv/HistoryDB-Web
python3 create_new_key.py

cd historydb
python3 manage.py makemigrations
python3 manage.py migrate
