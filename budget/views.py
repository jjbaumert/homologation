from datetime import datetime, date
import copy
from django.shortcuts import render
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Sum

from budget.models import HomologationItem, HomologationStatus
from budget.forms import StatusDateForm, StatusAmountForm, EditItemForm
from budget.tables import HomologationTable

from budget.templatetags.fyq import fyq

from django_tables2 import RequestConfig

#
#   find_quarter_start_fyq
#   
#   From a fiscal year/quarter return the first day of that 
#   quarter
#

def find_quarter_start_fyq(fyq_str, fyy_str):

    try:
        quarter_map = {
            '1': '10',
            '2': '1',
            '3': '4',
            '4': '7'
        }

        mon = quarter_map[fyq_str]
        yr = int(fyy_str)+2000

        if fyq_str =='1':
            yr = yr - 1
    except:
        raise AttributeError

    return datetime(year=int(yr),month=int(mon),day=1)

#
#   find_quarter_start
#
#   From a date find the first day of that quarter
#   If quarter offset is specified add (possibly a 
#   negative value) quarter offset to get to the 
#   real date.
#

def find_quarter_start(date_value, quarter_offset=0):
    
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

#
#   homologation_item_list
#
#   Display a list of HomologationItems
#

def homologation_item_list(request, list_filter='', qtr='', yr=''):

    today = date.today()
    title='Homologation Items'
    
    prev_quarter = None
    next_quarter = None

    #
    # Figure out what subset of the data to display.
    # Choices are all, current quarter, next quarter, 
    # previous quarter, or a quarter by name
    #

    if list_filter!='':
        if list_filter=='Q':
            title = "Q%sFY%s" % (qtr,yr)
            start_date = find_quarter_start_fyq(qtr,yr)
            end_date = find_quarter_start(start_date,1)
        elif list_filter=='last_quarter':
            title = 'Last Quarter'
            start_date = find_quarter_start(today,-1)
            end_date = find_quarter_start(today,0)
        elif list_filter=='this_quarter':
            title = 'Current Quarter'
            start_date = find_quarter_start(today)
            end_date = find_quarter_start(today,1)
        elif list_filter=='next_quarter':
            title = 'Next Quarter'
            start_date = find_quarter_start(today,1)
            end_date = find_quarter_start(today,2)
            
        if start_date >= datetime(year=2011, month=10, day=1): #jjb fixme... get rid of magic number
            prev_quarter = fyq(find_quarter_start(start_date,-1))

        next_quarter = fyq(end_date)
			
        data_set = HomologationStatus.objects.filter(
            active_record=True,
            requested_start__gte=str(start_date.date()),
            requested_start__lt=str(end_date.date()))
    else:
        #
        # If the user doesn't specify a filter, display all of the items >= 2011-10-01
        #
        
		data_set = HomologationStatus.objects.filter(
            active_record=True,
            requested_start__gte='2011-10-01')

    table = HomologationTable(data_set)

    #
    # Grab the totals
    #

    approval_totals = data_set.values('approval_status'). \
        annotate(budget_sum=Sum('budget_amount')). \
        order_by('-budget_sum')

    status_totals = data_set.values('certification_status'). \
        exclude(approval_status='cancelled'). \
        annotate(budget_sum=Sum('budget_amount')). \
        order_by('-budget_sum')

    type_totals = data_set.values('homologation_item__cert_type'). \
        exclude(approval_status='cancelled'). \
        annotate(budget_sum=Sum('budget_amount')). \
        order_by('-budget_sum')

    #
    # Display table using Django Tables2
    #

    RequestConfig(request).configure(table)

    return render(request, "budget/homologation_item_list.html", 
        { 'table': table,
          'title': title,
          'approval_totals': approval_totals,
          'status_totals': status_totals,
          'type_totals': type_totals,
          'prev_quarter': prev_quarter,
          'next_quarter': next_quarter})

#
#   budget_item
#

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
# update_statusrecord
#
# Update the status record and log the changes
#

def update_statusrecord(status, values):
    print values

    fields = status._meta.get_all_field_names()

    #
    # verify that the underlying fields are present
    #
    # jjb fixme: make into an assertion?
    #

    if not (fields.__contains__('id') and
            fields.__contains__('active_record') and 
            fields.__contains__('updated') and 
            fields.__contains__('update_reason')):
        raise AttributeError

    update_str = ""
    new_status = copy.deepcopy(status)

    #
    # Walk through each item_status items and make sure it is
    # part of HomologationStatus. If it has changed create a log entry
    #

    for key,value in values.iteritems():
        if not fields.__contains__(key):
            raise AttributeError

        if value != getattr(status,key):
            update_str = update_str + "%s from %s to %s\r\n" % (key,getattr(status,key),value)
            setattr(new_status,key,value)


    if update_str != "":
        #
        # Invalidate the id so we write a new record
        # Update the update text and date and write the new record
        #

        new_status.id = None
        new_status.active_record = True
        new_status.updated = datetime.now()
        new_status.update_reason = update_str
        new_status.save()

        #
        # Make the old record inactive
        #

        status.active_record = False
        status.save()


#
#   cert_status_map
#

cert_status_map = {
    # action           Name            cert/budget      date form   required 
    'quoting'      : [ 'Quoting',      'certification', False,      None ],     
    'ready'        : [ 'Ready',        'certification', True,       'ready' ],
    'submitting'   : [ 'Submitting',   'certification', False,      None],
    'in_progress'  : [ 'In-Progress',  'certification', True,       'started' ],
    'completed'    : [ 'Completed',    'certification', True,       'completed' ],
    'failed'       : [ 'Failed',       'certification', False,      None ],
    'cancelled'    : [ 'Cancelled',    'certification', False,      None ],
    'requested'    : [ 'Requested',    'budget',        True,       'requested_start' ],
    'approved'     : [ 'Approved',     'budget',        True,       'approved_for' ],
    'rejected'     : [ 'Rejected',     'budget',        False,      None ],
    'deferred'     : [ 'Deferred',     'budget',        False,      None ],
    'update_dates' : [ 'Dates',        'date',          True,       None ],
}

#
# Common function to update and log status and/or date changes
#

def update_status(item_status, item_id, action, form=None):

    #
    # Use the action to determine what status is changing
    #

    (status_string,cert_budget_or_date,_,_) = cert_status_map[action]

    update_list = {}

    if cert_budget_or_date == 'certification':
        update_list['certification_status'] = status_string
    elif cert_budget_or_date == 'budget':
        update_list['approval_status'] = status_string

    #
    # if we got something from the date form update the dates
    #

    if form != None:
        update_list.update(form.cleaned_data)

    #
    # update the record and redirect back to the editting the item
    #

    update_statusrecord(item_status, update_list)
    return HttpResponseRedirect("/budget/%s" % item_id)

#
#   amount_form
#

def amount_form(request, item_id):
    
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
    # If a date form is required generate it. Form is caught by
    # the POST code path below
    #

    if request.method == 'POST':

        #
        # Process the user input
        #

        form = StatusAmountForm(request.POST)

        if form.is_valid():
            update_statusrecord(item_status, form.cleaned_data)
            return HttpResponseRedirect("/budget/%s" % item_id)

        #
        # Note: we intentionally drop through to the render below the else
        #

    else:
            
        #
        # Generate the date form
        #

        initial_values = {
            'budget_amount' : item_status.budget_amount,
            'quoted_amount' : item_status.quoted_amount,
            'actual_amount' : item_status.actual_amount
        }
        
        form = StatusAmountForm(initial=initial_values)

    #
    # output the date input form
    #
        
    return render(request,'budget/homologation_item_amount.html',
        { 'form'        : form,
          'item'        : item,
          'item_status' : item_status })


def item_addform(request):
    if request.method == 'POST':
        form = EditItemForm(request.POST)

        if form.is_valid():
            item = HomologationItem()

            item.name = form.cleaned_data['name']
            item.description = form.cleaned_data['description']
            item.project_code = form.cleaned_data['project_code']
            item.cert_type = form.cleaned_data['cert_type']
            item.region = form.cleaned_data['region']
            item.supplier = form.cleaned_data['supplier']
            item.module = form.cleaned_data['module']

            item.save()

            item_status = HomologationStatus(homologation_item=item)
            item_status.approval_status = form.cleaned_data['approval_status']
            item_status.certification_status = form.cleaned_data['certification_status']
            item_status.budget_amount = form.cleaned_data['budget_amount']
            item_status.quoted_amount = form.cleaned_data['quoted_amount']
            item_status.actual_amount = form.cleaned_data['actual_amount']
            item_status.requested_start = form.cleaned_data['requested_start']
            item_status.ready         = form.cleaned_data['ready']
            item_status.approved_for  = form.cleaned_data['approved_for']
            item_status.started       = form.cleaned_data['started']
            item_status.completed     = form.cleaned_data['completed']

            item_status.updated = datetime.now()
            item_status.update_reason = "Initial Creation"

            item_status.save()
            
            return HttpResponseRedirect("/budget/%s" % item.id)
    else:
        form = EditItemForm()

    #
    # output the date input form
    #

    return render(request,'budget/homologation_item_edit.html',
        { 'form'        : form,
          'form_url'    : 'new',
          'title'       : "New Budget Item" })


#
#   item_form
#

def item_editform(request, item_id):
    
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
    # If a form is required generate it. Form is caught by
    # the POST code path below
    #

    if request.method == 'POST':

        #
        # Process the user input
        #

        #
        # jjb fixme: make sure that the dates follow the state
        #

        form = EditItemForm(request.POST)

        if form.is_valid():
            item.name = form.cleaned_data['name']
            item.description = form.cleaned_data['description']
            item.project_code = form.cleaned_data['project_code']
            item.cert_type = form.cleaned_data['cert_type']
            item.region = form.cleaned_data['region']
            item.supplier = form.cleaned_data['supplier']
            item.module = form.cleaned_data['module']
            item.save()

            item_status.homologation_item = item

            updated_values = {
                'approval_status': form.cleaned_data['approval_status'],
                'certification_status': form.cleaned_data['certification_status'],
                'budget_amount' : form.cleaned_data['budget_amount'],
                'quoted_amount' : form.cleaned_data['quoted_amount'],
                'actual_amount' : form.cleaned_data['actual_amount'],
                'requested_start' : form.cleaned_data['requested_start'],
                'ready'         : form.cleaned_data['ready'],
                'approved_for'  : form.cleaned_data['approved_for'],
                'started'       : form.cleaned_data['started'],
                'completed'     : form.cleaned_data['completed']
            }

            update_statusrecord(item_status, updated_values)

            return HttpResponseRedirect("/budget/%s" % item_id)

        #
        # Note: we intentionally drop through to the render below the else
        #

    else:
            
        #
        # Generate the date form
        #

        initial_values = {
            'name'          : item.name,
            'description'   : item.description,
            'project_code'  : item.project_code,
            'cert_type'     : item.cert_type,
            'region'        : item.region,
            'module'        : item.module,
            'supplier'      : item.supplier,
            'approval_status': item_status.approval_status,
            'certification_status': item_status.certification_status,
            'budget_amount' : item_status.budget_amount,
            'quoted_amount' : item_status.quoted_amount,
            'actual_amount' : item_status.actual_amount,
            'requested_start' : item_status.requested_start,
            'ready'         : item_status.ready,
            'approved_for'  : item_status.approved_for,
            'started'       : item_status.started,
            'completed'     : item_status.completed
        }
        
        form = EditItemForm(initial=initial_values)

    #
    # output the date input form
    #

    return render(request,'budget/homologation_item_edit.html',
        { 'form'        : form,
          'item'        : item,
          'item_status' : item_status,
          'form_url'    : "%d/edit" % item.id,
          'title'       : item.name }) 


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














