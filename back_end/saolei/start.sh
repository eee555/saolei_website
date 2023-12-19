#!/bin/bash
rm -r ../../font_end
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
cp -f default.conf /etc/nginx/conf.d/default.conf
sudo nginx -s reload
uwsgi --ini uwsgi.ini
