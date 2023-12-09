FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
COPY ./requirements.txt /code

WORKDIR /code

# RUN sed -i "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list
# RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list

# RUN apt-get clean && apt-get -y update
# RUN apt-get -y upgrade
# RUN apt-get -y install libsasl2-dev python-dev libldap2-dev libssl-dev libsnmp-dev

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --index-url https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt

# 去除windows系统编辑文件中多余的\r回车空格
RUN sed -i 's/\r//' ./start.sh

# 给start.sh可执行权限
RUN chmod +x ./start.sh

COPY ./* /code/
