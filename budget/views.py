# Create your views here.
from django.template import Context, Template, loader

from django.http import HttpResponse, Http404

from budget.models import HomologationItem, HomologationStatus

def budget_list(request):
	object_list = []
	
	data_set = HomologationItem.objects.filter(homologationstatus__requested_start__gte='2011-10-01').order_by('-homologationstatus__requested_start','-homologationstatus__budget_amount')
	
	for item in data_set:
		object_list.append({'item' : item,
							'status' : item.homologationstatus_set.order_by("-updated")[0]})
		
	t = loader.get_template('budget/homologation_item_list.html')	
	c = Context({'object_list' : object_list })
	
	return HttpResponse(t.render(c))
	
def budget_item(request, item_id):
	
	try:
		item = HomologationItem.objects.get(pk=item_id)
		item_status = item.homologationstatus_set.order_by("-updated")[0]
	except:
		raise Http404
	
	t = loader.get_template('budget/homologation_item_detail.html')
	c = Context({'item' : item, 'item_status' : item_status })
	
	return HttpResponse(t.render(c))
