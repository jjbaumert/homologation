from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'homologation.views.home', name='home'),
    # url(r'^homologation/', include('homologation.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^budget/', include('budget.urls')),
    url(r'^bom/', include('bommanage.urls')),
    url(r'^psr/', include('psr.urls')),
)
