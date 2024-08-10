#!/bin/bash
# 仅更新文章

# 从gitee下载文章静态资源
cd dist/article
git clone https://gitee.com/ee55/saolei_website_article.git
cp -r saolei_website_article/* ./
rm -r .git
rm LICENSE
rm -r saolei_website_article



