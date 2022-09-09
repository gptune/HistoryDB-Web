# HistoryDB-Web

The web interface for the GPTune history database repository for development and debugging.
The web framework is based on Django and uses Bootstrap for pretty webpages.

## Prerequisite and installation

- Python (version >= 3.7)

- Django installed (tested on version 3.2.4)
```
python -m pip install django==3.2.4
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
- django-docs
```
python -m pip install django-docs
```
- sphinx
```
python -m pip install sphinx
```
-- recommonmark
```
python -m pip install recommonmark
```
-- sphinx_rtd_theme
```
python -m pip install sphinx_rtd_theme
```
-- pycryptodome
```
pip install pycryptodome
```

- NOTE: please make sure your PYTHONPATH indicates Django, markdown, pymongo, djang-widget-tweaks modules.

- mongodb installed (Ubuntu)
```
$ sudo apt-get install -y wget
$ wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
$ sudo apt-get install -y gnupg
$ wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
$ echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
$ sudo apt-get update
$ sudo apt-get install -y mongodb-org
```

- mongodb installed (Mac)
```
$ brew tap mongodb/brew
$ brew install mongodb-community@4.0
```

- setup necessary information for our web features (1. Django secret key, 2. Admin email, 3. Google recaptcha (a robot checker))
```
$ python web-reset.py
```
A Django secret key is required to run the webapp. You can comment out lines 8-31 for simple testing (runs the webapp with no admin email/robot checker)

## Additional Python packages needed by Dashing integration (performance counter analysis)

-- plotly
```
pip install plotly
```
-- h5py
```
pip install h5py
```
-- psutil
```
pip install psutil
```
-- dash
```
pip install dash
```
-- kaleido
```
pip install kaleido
```

## Set environment

- Set location for database files
```
$ export HISTORYDB_STORAGE="Path to the database directory in HistoryDB-Web"
$ mkdir -p $HISTORYDB_STORAGE/sqlite_data
$ export HISTORYDB_SQLITE_DATA=$HISTORYDB_STORAGE/sqlite_data
$ mkdir -p $HISTORYDB_STORAGE/mongodb_data
$ export HISTORYDB_MONGODB_DATA=$HISTORYDB_STORAGE/mongodb_data
$ export HISTORYDB_JSON_DATA=$HISTORYDB_STORAGE
```

## Basic Django setting

- set SQLite DB for the Django application
```
cd historydb
$ python manage.py makemigrations
$ python manage.py migrate
```
- create an admin account for the Django application
```
cd historydb
$ python manage.py createsuperuser
```

## Run (testing/debugging mode)

- run MongoDB daemon: this daemon will hang in the terminal to wait for some events. You can use "mongod --dbpath "path" &" to run it as a background process.
```
$ mongod --dbpath $HISTORYDB_MONGODB_DATA
```

- run the Django web application
```
cd historydb
$ python manage.py runserver
```

access "http://localhost:8000" from a web browser (https is currently not supported)

## Note on user sign-up in the current test version

- User sign-up: When a user signs-up, the Django application try to send an activation code to the user email. It requires the sender email login credentials which are not in this Github repository for security. So, you will not receive an activation code via email unless you add login credentials in a file. Instead, the Django application will show the user activation code in your terminal which is running "$ python manage.py runserver". You can use it to complete the sign-up.

## Acknowledgement

GPTune Copyright (c) 2021, The Regents of the University of California, through
Lawrence Berkeley National Laboratory (subject to receipt of any required approvals
from the U.S.Dept. of Energy) and the University of California, Berkeley.
All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative
works, and perform publicly and display publicly, and to permit other to do so.
