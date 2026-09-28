# 假如有多个同名进程将不适用
sudo pkill -9 uwsgi || true

sudo pkill -9 -f db_worker || true
sudo pkill -9 -f runapscheduler || true

