from django.conf.urls import patterns, include, url

from budget import views

urlpatterns = patterns ('',
    url(r'^list$', views.budget_list),
)
