#!/bin/bash
rm -rf ../../font_end
rm -rf /root/saolei/static
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runapschedulermonitor
cp -f default.conf /etc/nginx/conf.d/default.conf
sudo nginx -s reload
uwsgi --ini uwsgi.ini
