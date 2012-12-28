from django.conf.urls import url, patterns

from budget import views

urlpatterns = patterns ('',
    url(r'^([0-9]{1,4})',views.budget_item),
    url(r'^list$', views.budget_list),
)
