# coding=utf-8
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saolei.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()


# django-admin startproject saolei
# python manage.py migrate
# python manage.py runserver            # 开发时启动服务，且不需要调试文章，不推荐；部署时启动服务。
# python manage.py runserver --nostatic # 开发时启动服务，且需要调试文章
# python manage.py startapp identifier  # 开新app
# pip install pymysql
# 修改__init__.py，  import pymysql    pymysql.install_as_MySQLdb()
# python manage.py migrate
# python manage.py makemigrations

# python manage.py createsuperuser
# 1，wangjianing@88.com，123456
# pip install  django-simple-captcha
# python manage.py makemigrations --empty msuser
# ALTER TABLE videomanager_expandvideomodel CHANGE identifier identifier varchar(255);
# ALTER TABLE msuser_userms CHANGE designators identifiers json;





