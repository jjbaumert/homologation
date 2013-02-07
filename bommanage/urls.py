from django.conf.urls import url, patterns

from bommanage import views

urlpatterns = patterns ('',
    url(r'^search$',views.search),
    url(r'^move$',views.move),
)
