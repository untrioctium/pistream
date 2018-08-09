from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^json/$', 'stream.views.appjson.dispatch'),
    url(r'^auth/$', 'stream.views.auth.auth'),
    url(r'^template/$', 'stream.views.template.dispatch'),
    url(r'^image/(?P<model>\w+)/(?P<id>\d+)/(?P<size>\w+)/$', 'stream.views.image.image'),
    url(r'^$', "stream.views.root.root"),
    url(r'^admin/', include(admin.site.urls)),
)
