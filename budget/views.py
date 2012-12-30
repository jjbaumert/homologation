from datetime import datetime, date

from django.shortcuts import render
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404

from budget.models import HomologationItem
from budget.forms import StatusDateForm



def find_quarter(date_value, quarter_offset=0):
	quarter_month = date_value.month
	quarter_year = date_value.year
	
	year_offset = int("%.*f" % (0, quarter_offset/4.0))
	quarter_offset = quarter_offset + year_offset*4

	if quarter_month>=10:
		quarter_month = 10 
	elif quarter_month >= 7:
		quarter_month = 7
	elif quarter_month >= 4:
		quarter_month = 4
	elif quarter_month >= 1:
		quarter_month = 1
		
	quarter_month = quarter_month + quarter_offset*3
	
	if quarter_month>12:
		quarter_year=quarter_year+1
		quarter_month=quarter_month-12
	elif quarter_month<1:
		quarter_year=quarter_year-1
		quarter_month=quarter_month+12
	
	return datetime(year=quarter_year+year_offset,month=quarter_month,day=1)
	



def budget_list(request, list_filter):
    object_list = []
	
    today = date.today()
    title = ''
	
    if list_filter!='':
		if list_filter=='last_quarter':
			title = 'Last Quarter'
			start_date = find_quarter(today,-1)
			end_date = find_quarter(today,0)
		elif list_filter=='this_quarter':
			title = 'Current Quarter'
			start_date = find_quarter(today)
			end_date = find_quarter(today,1)
		elif list_filter=='next_quarter':
			title = 'Next Quarter'
			start_date = find_quarter(today,1)
			end_date = find_quarter(today,2)
			
		data_set = HomologationItem.objects.filter(
            homologationstatus__active_record=True,
            homologationstatus__requested_start__gte=str(start_date.date()),
			homologationstatus__requested_start__lt=str(end_date.date())).order_by(
                '-homologationstatus__requested_start',
                '-homologationstatus__budget_amount')
    else:
		data_set = HomologationItem.objects.filter(
            homologationstatus__active_record=True,
            homologationstatus__requested_start__gte='2011-10-01').order_by(
                '-homologationstatus__requested_start',
                '-homologationstatus__budget_amount')
	
    for item in data_set:
		object_list.append(
            {'item' : item,
			 'status' : item.homologationstatus_set.order_by("-updated")[0],
             'title' : title})
		
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

#
#   budget_status
#   dead --- delete
#

def budget_status(request, item_id, action):
    status_map = {
        'requested' : 'Requested',
        'approved'  : 'Approved',
        'rejected'  : 'Rejected',
        'deferred'  : 'Deferred'
    }

    if not status_map.__contains__(action):
        raise Http404

    status_string = status_map[action]

    item = HomologationItem.objects.get(pk=item_id)
    item_status = item.homologationstatus_set.order_by("-updated")[0]

    if not item_status.approval_status == status_string:
        item_status.id = None
        item_status.updated = datetime.now()
        item_status.update_reason = "Moved approval status to: %s from: %s" % \
            (status_string,item_status.approval_status)
        item_status.approval_status = status_string
        item_status.save()

    return HttpResponseRedirect("/budget/%s" % item_id)



cert_status_map = {
    # action           Name            cert/budget      date form   required 
    'quoting'      : [ 'Quoting',      'certification', False,      None ],     
    'ready'        : [ 'Ready',        'certification', True,       'ready'  ],
    'submitting'   : [ 'Submitting',   'certification', False,      None],
    'in_progress'  : [ 'In-Progress',  'certification', True,       'started'  ],
    'completed'    : [ 'Completed',    'certification', True,       'comleted'  ],
    'passed'       : [ 'Passed',       'certification', False,      None ],
    'failing'      : [ 'Failing',      'certification', False,      None ],
    'failed'       : [ 'Failed',       'certification', False,      None ],
    'cancelled'    : [ 'Cancelled',    'certification', False,      None ],
    'requested'    : [ 'Requested',    'budget',        True,       'requested_start'  ],
    'approved'     : [ 'Approved',     'budget',        True,       'approved_for'  ],
    'rejected'     : [ 'Rejected',     'budget',        False,      None ],
    'deferred'     : [ 'Deferred',     'budget',        False,      None ],
    'update_dates' : [ 'Dates',        'date',          True,       None ],
}


#
# Common function to update and log status and/or date changes
#

def update_status(item_status, item_id, action, form=None):
    (status_string,cert_budget_or_date,_,_) = cert_status_map[action]

    print item_status, item_id, action, form

    #
    # Mark the old status as invalid
    #

    item_status.active_record=False
    item_status.save()

    #
    # Create a new active record by marking the id as None
    #


    item_status.id = None
    item_status.active_record=True

    #
    # Update the log information
    #
    
    #
    # jjb fixme: decide what to do with log when we are only
    # updateing the dates.
    #

    item_status.updated = datetime.now()

    if cert_budget_or_date == 'certification':
        old_status = item_status.certification_status
        item_status.certification_status = status_string
    elif cert_budget_or_date == 'budget':
        old_status = item_status.approval_status
        item_status.approval_status = status_string

    item_status.update_reason = "Moved %s status to: %s from: %s" % \
        (cert_budget_or_date,status_string,old_status)

    #
    # if we got something from the date form update the dates
    #

    if form != None:
        item_status.requested_start = form.cleaned_data['requested_start']
        item_status.approved_for = form.cleaned_data['approved_for']
        item_status.ready = form.cleaned_data['ready']
        item_status.started = form.cleaned_data['started']
        item_status.completed = form.cleaned_data['completed']

    item_status.save()

    #
    # redirect back to the editting the item
    #

    return HttpResponseRedirect("/budget/%s" % item_id)


#
#   cert_status
#
#   Update the certification status and where appropriate dates
#

def cert_status(request, item_id, action):
    
    #
    # if it is an invalid action return 404
    #

    if not cert_status_map.__contains__(action):
        raise Http404

    #
    # Grab the update options from cert_status_map
    #

    (status_string, 
     cert_budget_or_date, 
     date_form_required,
     required_field) = cert_status_map[action]

    #
    # Load the item and the most recent item_status
    #   jjb fixme: should this raise a 404 or redirect?
    #

    try:
        item = HomologationItem.objects.get(pk=item_id)
        item_status = item.homologationstatus_set.order_by("-updated")[0]
    except:
        raise Http404

    #
    # if we are not really changing the status, just redirect
    # jjb fixme --- is this a good workflow? Just eliminate?
    #

    if item_status.approval_status == cert_status_map[action]:
        return HttpResponseRedirect("/budget/%s" % item_id)

    #
    # If a date form is required generate it. Form is caught by
    # the POST code path below
    #

    if date_form_required:
        if request.method == 'POST':

            #
            # Process the user input
            # jjb fixme... need to make the date field requested manditory
            #

            form = StatusDateForm(request.POST)

            if required_field:
                form.fields[required_field].required=True

            if form.is_valid():
                return update_status(item_status, item_id, action, form)

            #
            # Note: we intentionally drop through to the render below the else
            #

        else:
            
            #
            # Generate the date form
            #

            initial_values = {
                'requested_start' : item_status.requested_start,
                'approved_for'    : item_status.approved_for,
                'ready'           : item_status.ready,
                'started'         : item_status.started,
                'completed'       : item_status.completed
            }
        
            form = StatusDateForm(initial=initial_values)

        #
        # output the date input form
        #
        
        return render(request,'budget/homologation_item_date.html',
            { 'action'      : action,
              'form'        : form,
              'item'        : item,
              'item_status' : item_status })
    else:
        
        #
        # If no update is required just create the new status record
        #

        return update_status(item_status, item_id, action)


#
#   item history
#
#   Output a list of HomologationItem with the current active status
#


def item_history(request, item_id):
	try:
		item = HomologationItem.objects.get(pk=item_id)
		item_statuses = item.homologationstatus_set.order_by("-updated")
	except:
		raise Http404
	
	t = loader.get_template('budget/homologation_item_history.html')
	c = Context({'item' : item, 'item_statuses' : item_statuses })
	
	return HttpResponse(t.render(c))














