# saolei_website

新扫雷网，雏形
Vue3+Ts+Element-ui+Django+Mysql

已完成：注册登录、上传录像、录像查询（排序、分页）、修改头像姓名个性签名。

下一步计划做：前端解析录像、个人主页展示记录、用户排行榜、首页破记录消息。

项目安装流程：

后端：
1. pip install -r requirements.txt
1. 安装mysql，创建名为saolei的数据库
1. python manage.py makemigrations
1. py -3 manage.py migrate
1. py -3 manage.py runserver

前端：
1. npm install
1. npm run serve

