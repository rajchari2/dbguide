"""dbguide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from dbguide.views import home
from dbguide.views import submit
from dbguide.views import publications
from dbguide.views import template
from dbguide.views import plasmidsandprotocols

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?i)dbguide/', home, name='home'),
    url(r'^(?i)submit/$', submit ,name='submit'),
    url(r'^(?i)publications/$', publications ,name='publications'),
    url(r'^(?i)template/$', template ,name='template'),
    url(r'^(?i)plasmidsandprotocols/$', plasmidsandprotocols ,name='plasmidsandprotocols'),
    url(r'^$', home, name='home'), 
]
