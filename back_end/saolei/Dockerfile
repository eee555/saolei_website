FROM python:3.10

LABEL maintainer="wangjn@88.com"

#设置环境变量
ENV PYTHONUNBUFFERED 1

#设置pip源为国内源
COPY pip.conf /root/.pip/pip.conf

#在容器内/var/www/html/下创建mysite1文件夹
RUN mkdir -p /var/www/html/saolei

#设置容器内工作目录
WORKDIR /var/www/html/saolei

#将当前目录文件加入到容器工作目录中(.表示当前宿主机目录)
ADD . /var/www/html/saolei

#利用pip安装依赖
RUN pip install -r requirements.txt