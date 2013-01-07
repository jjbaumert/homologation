from django.conf.urls import url, patterns

from budget import views

urlpatterns = patterns ('',
    url(r'^([0-9]{1,4}$)',views.budget_item),
    url(r'^list/(last_quarter|this_quarter|next_quarter|)$', views.homologation_item_list),
    url(r'^list/(Q)([1-4])FY(11|12|13)$', views.homologation_item_list),

    url(r'^([0-9]{1,4})/(requested|approved|deferred|rejected)',views.cert_status),
    url(r'^([0-9]{1,4})/(quoting|ready|in_progress|completed|failed|cancelled)',views.cert_status),
    url(r'^new$',views.item_addform),
    url(r'^([0-9]{1,4})/edit',views.item_editform),
    url(r'^([0-9]{1,4})/edit_amount',views.amount_form),
    
    url(r'^([0-9]{1,4})/history$',views.item_history),
)
