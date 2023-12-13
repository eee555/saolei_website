#!/bin/bash
# 传入版本号

wget "https://gitee.com/ee55/saolei_website/releases/download/$1/dist.zip"
rm -r dist
unzip dist.zip
rm dist.zip
rm -r /root/saolei
python3 manage.py collectstatic



