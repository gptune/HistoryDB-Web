# HistoryDB-Web

The web interface for the GPTune history database repository for development and debugging.
The web framework is based on Django and uses Bootstrap for pretty webpages.

## Prerequisite

- Python (version higher than 3)
- Django installed
- MongoDB installed (although the current version has not integrated MongoDB yet)
- markdown (pip install markdown)

- create your own Django secret key

cd HistoryDB-Web

$ python create\_new\_key.py

- set SQLite DB

cd historydb

$ python manage.py makemigrations

$ python manage.py migrate

## Run (testing/debugging mode)

cd dbfiles

$ mkdir dbfiles

$ mongod --dbpath $PWD/dbfiles &

cd ../historydb

$ python manage.py runserver

access "https://localhost:8000" from a web browser
