# <a href="https://github.com/eee555/saolei_website" >开源扫雷网（OPEN MINESWEEPER WEBSITE
）</a>


[![saolei_website](https://img.shields.io/badge/saolei_website-v1.7-brightgreen.svg)](https://github.com/eee555/Solvable-Minesweeper)
[![stars](https://img.shields.io/github/stars/eee555/saolei_website)](https://github.com/eee555/saolei_website/stargazers)
[![forks](https://img.shields.io/github/forks/eee555/saolei_website)](https://github.com/eee555/saolei_website/forks)

[English](Readme_en.md)

前端：Vue3 + Ts + Element-ui + wasm-bindgen  
后端：Django + Mysql + redis  
部署：Nginx + uwsgi  
安全：百度大脑  

## 最新进展
:white_check_mark: 开发核心功能  
:white_check_mark: 租赁服务器  
:white_check_mark: 初步部署  
:white_check_mark: 租赁域名  
:white_check_mark: 备案  
:white_check_mark: 删档内测  
:black_square_button: 删档公测  
:black_square_button: 上线  


## 项目安装流程：

本项目可在windows上开发，在Linux上部署。开发调试步骤如下：首先将项目克隆到本地，例如E://saolei_website下

后端：
1. cd saolei_website\back_end\saolei
1. pip install -r requirements.txt
1. 安装mysql，根据saolei_website\back_end\saolei\saolei\setting.py中的配置，（默认）创建名为saolei的数据库，用户名root，密码123456
1. 新建一个文件夹saolei_website\back_end\saolei\logs（用来存放日志）
1. 新建一个文件夹saolei_website\back_end\saolei\assets（存放录像、头像、文章）
1. （可选，假如需要看文章）在saolei_website\back_end\saolei\assets下执行`git clone https://gitee.com/ee55/saolei_website_article.git`，并将文件夹名由saolei_website_article改为article
1. python manage.py makemigrations
1. python manage.py migrate
1. python manage.py runserver
1. （可选，假如要启动定时任务，不做相关功能时可以不启动）python manage.py runapschedulermonitor

前端：
1. 从[https://github.com/eee555/flop-player/releases/download/v1.1/dist.zip](https://github.com/eee555/flop-player/releases/download/v1.1/dist.zip)下载新版flop播放器，并解压到saolei_website\front_end\public\flop下（将文件夹的名称dist修改为flop），使得saolei_website\front_end\public\flop\index.html能够被找到
1. cd saolei_website\front_end
1. 如果使用npm，则npm install；如果知道什么是yarn且使用yarn，则yarn
1. 如果使用npm，则npm run dev；如果知道什么是yarn且使用yarn，则yarn dev

特殊的调试参数：位于`backend\saolei\config\flags.py`

## 链接




## 赞助
感谢您考虑支持我们的开源项目，赞助时请备注您的称呼。您的赞助将有助于项目的持续发展和改进，使我们能够继续提高软件的质量（owner许诺向所有contributor按合理的比例分配赞助得到的收入）。  
### 一般赞助者
- 一次性捐款￥10或以上
- 您的名字将出现在项目的贡献者列表中

### 核心赞助者
- 一次性捐款￥50或以上
- 您的名字将出现在项目的贡献者列表中
- 独家定期报告项目进展  

![](readme_pic/微信收款码.png) ![](readme_pic/支付宝收款码.png)  

