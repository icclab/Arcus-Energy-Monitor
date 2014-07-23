from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'charts.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$','happycharts.views.home'),
    url(r'^getenergydata$','happycharts.views.getenergycomsuption'),
    url(r'^getmeters$','happycharts.views.getmeters'),
    url(r'^getinstance$','happycharts.views.ceilometer_get_instances'),
    url(r'^charts/$','happycharts.views.init'),
    url(r'^admin/', include(admin.site.urls)),
)
