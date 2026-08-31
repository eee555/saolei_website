#!/bin/bash
rm -rf /root/saolei/static
# 搜集静态文件到/root/saolei/static，按照setting的配置，只有dist
echo "开始搜集静态文件，大约20秒..."
python3 manage.py collectstatic --noinput
echo "静态文件搜集完成。"
# 前端文件的打包结果来自github工作流
python3 manage.py makemigrations
python3 manage.py migrate

if [ "${START_DB_WORKER:-1}" = "1" ]; then
    mkdir -p logs
    echo "Starting db_worker after ${DB_WORKER_START_DELAY:-10}s..."
    (
        sleep "${DB_WORKER_START_DELAY:-10}"
        if command -v ionice >/dev/null 2>&1; then
            exec nice -n "${DB_WORKER_NICE:-10}" ionice -c2 -n7 python3 manage.py db_worker_robust --interval "${DB_WORKER_INTERVAL:-2}"
        fi
        exec nice -n "${DB_WORKER_NICE:-10}" python3 manage.py db_worker_robust --interval "${DB_WORKER_INTERVAL:-2}"
    ) >> logs/db_worker.log 2>&1 &
    echo "db_worker scheduled."
else
    echo "Skipping db_worker because START_DB_WORKER=${START_DB_WORKER}."
fi

cp -f default.conf /etc/nginx/conf.d/default.conf
sudo nginx -s reload
uwsgi --ini uwsgi.ini
