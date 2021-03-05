FROM debian:stable

RUN apt-get update
RUN apt-get install git -y

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN python3 -m pip install django
RUN python3 -m pip install markdown
RUN python3 -m pip install pymongo
RUN python3 -m pip install django-widget-tweaks
RUN python3 -m pip install django-docs
RUN python3 -m pip install sphinx
RUN python3 -m pip install recommonmark
RUN python3 -m pip install sphinx_rtd_theme

RUN apt-get install -y wget
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
RUN apt-get install -y gnupg
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN apt-get update
RUN apt-get install -y mongodb-org

RUN apt-get install -y vim

RUN git clone https://github.com/gptune/HistoryDB-Web /srv/HistoryDB-Web
RUN git clone https://github.com/gptune/HistoryDB-Web /srv/HistoryDB-Docs
