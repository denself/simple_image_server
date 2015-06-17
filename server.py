# -*- coding: utf-8 -*-
import hashlib
import os
import sys
from io import BytesIO
from PIL import Image, ImageDraw
from django.conf import settings

__author__ = 'Denis Ivanets (denself@gmail.com)'

BASE_DIR = os.path.dirname(__file__)
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
    ),
    INSTALLED_APPS=(
        'django.contrib.staticfiles',
    ),
    STATIC_URL='/static/',
    STATIC_ROOT = BASE_DIR,
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder"
    ),
    TEMPLATE_DIRS=(
        os.path.join(BASE_DIR, 'templates'),
    ),
)


from django import forms
from django.conf.urls import url
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import etag


class ImageForm(forms.Form):
    """This form validates requested image"""

    height = forms.IntegerField(min_value=1, max_value=2000)
    width = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format='PNG'):
        """Generate an image of requested type and return as raw bytes"""
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        key = '{}.{}.{}'.format(width, height, image_format)
        content = cache.get(key)
        if content is None:
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            text = '{} x {}'.format(width, height)
            text_width, text_height = draw.textsize(text)
            if text_width <= width and text_height <= height:
                text_top = (height - text_height) // 2
                text_left = (width - text_width) // 2
                draw.text((text_left, text_top), text, fill=(255, 255, 255))
            content = BytesIO()
            image.save(content, image_format)
            content.seek(0)
            cache.set(key, content, 60*60)
        return content


def generate_etag(request, width, height):
    content = 'Placeholder {0} x {1}'.format(width, height)
    return hashlib.sha1(content.encode('utf-8')).hexdigest()


@etag(generate_etag)
def placeholder(request, width, height):
    form = ImageForm({'width': width, 'height': height})
    if form.is_valid():
        image = form.generate()
        return HttpResponse(image, content_type='image/png')
    else:
        return HttpResponseBadRequest('Invalid Image requested')


def index(request):
    example = reverse('placeholder', kwargs={'width': 50, 'height': 50})
    context = {
        'example': request.build_absolute_uri(example),
    }
    return render(request, 'home.html', context)


urlpatterns = (
    url(r'^image/(?P<width>\d+)x(?P<height>\d+)/$', placeholder,
        name='placeholder'),
    url(r'^$', index, name='home'),
)

application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)