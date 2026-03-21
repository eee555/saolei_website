# 假如有多个同名进程将不适用
sudo pkill -9 uwsgi || true

sudo pkill -9 db_worker || true
sudo pkill -9 runapschedulermonitor || true
sudo pkill -9 runapscheduleruserprofile || true
sudo pkill -9 runapschedulervideomanager || true

