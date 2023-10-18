# saolei_website
# 新扫雷网

前端：Vue3 + Ts + Element-ui + wasm-bindgen  
后端：Django + Mysql + redis  

已完成：注册登录、上传录像、录像查询（排序、分页）、修改头像姓名个性签名、查询排行榜、权限系统、审核队列、最新录像。

下一步计划做：稳定性优化、首页破记录消息。

项目安装流程：

首先将项目克隆到本地，例如E://saolei_website下

后端：
1. cd saolei_website\back_end\saolei
1. pip install -r requirements.txt
1. 安装mysql，根据saolei_website\back_end\saolei\saolei\setting.py中的配置，创建名为saolei的数据库，用户名root，密码123456
1. 把所有migrations文件夹（例如msuser\migrations等）下的诸如"0001_initial.py"的开头是数字的.py文件删除
1. python manage.py makemigrations
1. python manage.py migrate
1. python manage.py runserver

前端：
1. 从[https://github.com/hgraceb/flop-player/releases](https://github.com/hgraceb/flop-player/releases)下载flop播放器，并解压到saolei_website\front_end\public\flop下，使得saolei_website\front_end\public\flop\index.html能够被找到
1. cd saolei_website\front_end
1. npm install
1. npm run serve

