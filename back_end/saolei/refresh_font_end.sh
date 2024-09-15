#!/bin/bash
# 传入版本号

# 拟弃用，改为github打包

wget "https://gitee.com/ee55/saolei_website/releases/download/$1/dist.zip"
rm -r dist
unzip dist.zip
rm dist.zip
mkdir dist/article

# 从gitee下载文章静态资源
cd dist/article
git clone https://gitee.com/ee55/saolei_website_article.git
cp -r saolei_website_article/* ./
rm -r .git
rm LICENSE
rm -r saolei_website_article
cd ..
cd ..

rm -r /root/saolei/static
python3 manage.py collectstatic



