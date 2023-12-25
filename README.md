# saolei_website
# 新扫雷网

前端：Vue3 + Ts + Element-ui + wasm-bindgen  
后端：Django + Mysql + redis  
部署：Nginx + uwsgi  

## 最新进展
:white_check_mark: 开发核心功能  
:white_check_mark: 租赁服务器  
:white_check_mark: 初步部署  
:white_check_mark: 租赁域名  
:black_square_button: 备案  
:black_square_button: 删档内测  
:black_square_button: 删档公测  
:black_square_button: 上线  


## 项目安装流程：

本项目可在windows上开发，在Linux上部署。开发调试步骤如下：首先将项目克隆到本地，例如E://saolei_website下

后端：
1. cd saolei_website\back_end\saolei
1. pip install -r requirements.txt
1. 安装mysql，根据saolei_website\back_end\saolei\saolei\setting.py中的配置，（默认）创建名为saolei的数据库，用户名root，密码123456
1. 建立一个文件夹saolei_website\back_end\saolei\logs（用来存放日志）
1. python manage.py makemigrations
1. python manage.py migrate
1. python manage.py runserver

前端：
1. 从[https://github.com/hgraceb/flop-player/releases](https://github.com/hgraceb/flop-player/releases)下载flop播放器，并解压到saolei_website\front_end\public\flop下，使得saolei_website\front_end\public\flop\index.html能够被找到
1. cd saolei_website\front_end
1. npm install
1. npm run serve

