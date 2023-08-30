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
# python manage.py runserver 8080
# python manage.py startapp polls
# pip install pymysql
# 修改__init__.py，  import pymysql    pymysql.install_as_MySQLdb()
# python manage.py migrate
# python manage.py makemigrations polls

# python manage.py createsuperuser
# 18201，2234208506@qq.com，6s51!f%^ds#65=f6
# pip install  django-simple-captcha




