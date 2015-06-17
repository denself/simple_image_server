# -*- coding: utf-8 -*-
import os
import sys
from django.conf import settings

__author__ = 'Denis Ivanets (denself@gmail.com)'

TEST_SECRET_KEY = '(j3t0hye(j4tcvl&-0q7isq7f4wrz4_h=hfq4wdll77j^ztv!o'
settings.configure(
    DEBUG=os.environ.get('DEBUG', 'on') == 'on',
    SECRET_KEY=os.environ.get('SECRET_KEY', TEST_SECRET_KEY),
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=os.environ.get('ALLOWED_HOSTS', 'localhost').split(','),
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )
)


from django import forms
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse


class ImageForm(forms.Form):
    """This form validates requested image"""

    height = forms.IntegerField(min_value=1, max_value=2000)
    width = forms.IntegerField(min_value=1, max_value=2000)


def placeholder(request, width, height):
    form = ImageForm({'width': width, 'height': height})
    if form.is_valid():
        height = form.cleaned_data['height']
        width = form.cleaned_data['width']
        return HttpResponse('Ok')
    else:
        return HttpResponse('Invalid Image requested')


def index(request):
    return HttpResponse('Hello world')


urlpatterns = (
    url(r'^image/(?P<width>\d+)x(?P<height>\d+)/$', placeholder),
    url(r'^$', index),
)

application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)