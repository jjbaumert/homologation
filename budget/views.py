# Create your views here.

from django.http import HttpResponse
from budget.models import HomologationItem, HomologationStatus

def budget_list(request):

	str = "<table>\r\n"
	for item in HomologationItem.objects.all():
		str = str + "\t<tr><td>" + item.name + "</td></tr>\r\n"
	str = str + "</table>\r\n"
	
	return HttpResponse(str)
