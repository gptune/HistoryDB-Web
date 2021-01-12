# HistoryDB-Web

The web interface for the GPTune history database repository for development and debugging.
The web framework is based on Django and uses Bootstrap for pretty webpages.

## Prerequisite and installation

- Python (version >= 3.7)
- Django installed
```
python -m pip install django
```
- markdown installed
```
python -m pip install markdown
```
- pymongo installed
```
python -m pip install pymongo
```
- django-widget-tweaks
```
python -m pip install django-widget-tweaks
```
- mongodb installed
```
$ sudo apt-get install -y wget
$ wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
$ sudo apt-get install -y gnupg
$ wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
$ echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
$ sudo apt-get update
$ sudo apt-get install -y mongodb-org
```

- create your own Django secret key
```
$ python create_new_key.py
```
- set SQLite DB for the Django project
```
cd historydb
$ python manage.py makemigrations
$ python manage.py migrate
```
## Run (testing/debugging mode)

- run MongoDB daemon
```
mkdir "whateverpath"
cd "whateverpath"
$ mkdir "whateverpath"
$ mongod --dbpath "whateverpath" 
```
- run Django web framework
```
cd historydb
$ python manage.py runserver
```

access "https://localhost:8000" from a web browser
