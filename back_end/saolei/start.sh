#!/bin/bash
rm -rf /root/saolei/static
# 搜集静态文件到/root/saolei/static，按照setting的配置，只有dist
echo "开始搜集静态文件，大约20秒..."
python3 manage.py collectstatic --noinput
echo "静态文件搜集完成。"
# 前端文件的打包结果来自github工作流
python3 manage.py makemigrations
python3 manage.py migrate

echo "Starting db_worker..."
nohup python3 manage.py db_worker & 
echo "db_worker started."

cp -f default.conf /etc/nginx/conf.d/default.conf
sudo nginx -s reload
uwsgi --ini uwsgi.ini
