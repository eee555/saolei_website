# <a href="https://github.com/eee555/saolei_website" >元扫雷网（Meta Saolei Website）</a>


[![saolei_website](https://img.shields.io/badge/saolei_website-v1.7-brightgreen.svg)](https://github.com/eee555/Solvable-Minesweeper)
[![stars](https://img.shields.io/github/stars/eee555/saolei_website)](https://github.com/eee555/saolei_website/stargazers)
[![forks](https://img.shields.io/github/forks/eee555/saolei_website)](https://github.com/eee555/saolei_website/forks)


Front end：Vue3 + Ts + Element-ui + wasm-bindgen  
Back end：Django + Mysql + redis  
Deployment：Nginx + uwsgi  
Censorship：百度大脑  

## Project status
:white_check_mark: Develop core functionalities  
:white_check_mark: Rent server  
:white_check_mark: Deploy for the first time  
:white_check_mark: Rent a domain name  
:white_check_mark: Registration  
:black_square_button: Alpha testing  
:black_square_button: Beta testing  
:black_square_button: Release  


## Steps for deployment：

This project can be developed on Windows and deployed on Linux. First, clone the project locally, say `E://saolei_website`.

Back end:
1. `cd saolei_website\back_end\saolei`
1. `pip install -r requirements.txt`
1. Install MySQL. According to configurations in `saolei_website\back_end\saolei\saolei\setting.py`, create a database named `saolei`, with username `root` and password `123456`
1. Create folder `saolei_website\back_end\saolei\logs`
1. `python manage.py makemigrations`
1. `python manage.py migrate`
1. `python manage.py runserver`

Front end:
1. Download the latest flop player from [https://github.com/eee555/flop-player/releases/download/v1.1/dist.zip](https://github.com/eee555/flop-player/releases/download/v1.1/dist.zip) and unzip it to `saolei_website\front_end\public\flop` (rename the folder name `dist` to `flop`), such that `saolei_website\front_end\public\flop\index.html` is accessible.
1. `cd saolei_website\front_end`
1. `npm install`
1. `npm run serve`

Special debugging parameters: 
1. `EMAIL_SKIP` from `saolei_website\backend\saolei\saolei\settings.py` can skip email captcha at user registration.

## Sponsor
TODO
