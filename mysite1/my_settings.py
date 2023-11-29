#  my_settings.py
import os
from pathlib import Path
DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DATABASE 명',
        'USER': 'DB접속 계정명',	#'root'
        'PASSWORD': 'DB접속용 비밀번호',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
SECRET_KEY = "django-insecure-1nk)q2hgiep5m#+!6$r%mlll^zoq2k$1lnpyy@bdsj-&bm#zy#"
