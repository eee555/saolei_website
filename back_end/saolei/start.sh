#!/bin/bash
rm -rf ../../font_end
rm -rf /root/saolei/static
# 搜集静态文件到/root/saolei/static，按照setting的配置，只有dist
python3 manage.py collectstatic --noinput
# 前端文件的打包结果来自github工作流
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runapschedulermonitor
cp -f default.conf /etc/nginx/conf.d/default.conf
sudo nginx -s reload
uwsgi --ini uwsgi.ini
