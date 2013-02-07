# Create your views here.

DIRECTORY_55M = '/mnt/55000000'
DIRECTORY_SEPARATOR = '/'

import os
import time

from django.shortcuts import render
from bommanage.forms import BomSearchForm

#--------------------------------------------------------------------
#
#   get_partchoices(prefix)
#
#--------------------------------------------------------------------
#
#   Get a list of the part number choices with the provided prefix
#
#--------------------------------------------------------------------

def get_partchoices(prefix):
    part_numberlist = ()

    #
    # get a list of the 55M parts in pending
    #

    part_folders=os.listdir(DIRECTORY_55M)

    #
    # create a tuple of tuples that can be directly used
    # for choices in a Django field
    #

    for part in part_folders:
        if part.find(prefix) == 0:
            part_numberlist += ((part,part),)

    return part_numberlist


#--------------------------------------------------------------------
#
#   get_fileinfo(directory)
#
#--------------------------------------------------------------------
#
#   Get a list of the part number choices with the provided prefix
#
#--------------------------------------------------------------------

def get_fileinfo(directory):
    file_list = []

    for file_name in os.listdir(directory):
        if file_name != 'Thumbs.db':
            qualified_file=directory+DIRECTORY_SEPARATOR+file_name
            if os.path.isdir(qualified_file):
                file_list += get_fileinfo(qualified_file)
            else:
                file_list += [(file_name,os.path.getmtime(qualified_file))]

    return file_list


#--------------------------------------------------------------------
#
#   ready_move(part_number)
#
#--------------------------------------------------------------------
#
#   verify the parts then move them from pending to released
#
#--------------------------------------------------------------------

class DateOutOfRange(Exception):
    pass

def ready_move(part_number):
    files = get_fileinfo(DIRECTORY_55M+DIRECTORY_SEPARATOR+part_number)

    time_list = []

    for file_info in files:
        (file_name, file_mtime) = file_info
        
        #
        # skip PDFs which can be generated after the fact through
        # a manual process
        #

        if file_name[-3:]!='pdf':
            time_list += [ file_mtime ]

    #
    # No files then return an error
    #

    if len(time_list)==0:
        return (False,"<p>Part Number: %s - Nothing to move</p>\n" % part_number)

    #
    # calculate the smallest, largest, and median times
    #
    
    time_list.sort()
    largest = max(time_list)
    smallest = min(time_list)
    rough_median = time_list[len(time_list)/2]

    #
    # if the largest and smallest are more than 4 minutes generate an error
    #

    if ((largest-smallest)/60) > 4:
        log_html = """
            <table>
                <tr><td>Part Number:</td><td>%s</td><td></td></tr>
                <tr><td colspan="3"><tr></td></tr>
        """ % part_number

        #
        # for each file show the file, file date and an error if >2 min of the median
        #

        for file_info in files:
            (file_name, file_mtime) = file_info
        
            error = ""
            if abs(file_mtime-rough_median)/60>2 and file_name[-3:]!='pdf':
                error = ">2 minutes off of median file date"

            log_html += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (
                file_name,
                time.strftime("%d %b %Y %H:%M:%S",time.gmtime(file_mtime)),
                error
            )

        log_html += "</table>\n"
        return (False,log_html)

    else:

        #
        # Success!
        #
    
        return (True,"<p>Part Number: %s - OK</p>\n" % part_number)
        


#--------------------------------------------------------------------
#
#   search(request)
#
#--------------------------------------------------------------------
#
#   Process a /bom/search request. Look up the part number and 
#   return the /bom/search with a list of possible parts that match.
#
#   When the user has selected the parts they will be redirected to 
#   the /bom/move for the processing of the specific parts.
#
#--------------------------------------------------------------------

def search(request):
    if request.method == 'POST':
        form = BomSearchForm(request.POST)

        #
        # verify we have a valid part number
        #

        if form.is_valid():
            part_number = form.cleaned_data['part_number']
            
            form.fields['possibilities'].choices = get_partchoices(part_number)

            #
            # drop through and render the search form with the new parts
            #
    else:
        form = BomSearchForm()

    #
    # Render the search form
    #

    return render(request,'bommanage/search.html', { 
        'form' : form, 
        'parts_to_select' : len(form.fields['possibilities'].choices)>0
    })


#--------------------------------------------------------------------
#
#   move(request)
#
#--------------------------------------------------------------------
#
#   Process a /bom/move request. Look up all of the possible parts
#   and make sure that the requested parts are included. For each
#   possible part move the part from pending to released and log
#   the result.
#
#--------------------------------------------------------------------

def move(request):
    if request.method == 'POST':
        form = BomSearchForm(request.POST)

        #
        # Allow any possible directory for validation of the form
        #

        form.fields['possibilities'].choices = get_partchoices('55')

        if form.is_valid():
            status = True
            log = ""

            #
            # Grab the parts to process. For each part see if the
            # move would be successful and accumulate the log
            #

            possibilities = form.cleaned_data['possibilities']

            for part_number in possibilities:
                (part_status, part_log) = ready_move(part_number)

                status &= part_status
                log += "<hr>"+part_log

            #
            # Execute the move
            #

            if status:
                for part_number in possibilities:
                    print "move %s from pending to released" % part_number

            #
            # Display the result 
            #

            return render(request,'bommanage/move_result.html', {
                'status':status,
                'log':log
            })
                
        else:
            
            #
            # if we received an invalid form render the 
            # search form.
            #

            return render(request,'bommanage/search.html', { 
                'form':form, 
                'parts_to_select':len(form.fields['possibilities'].choices)>0
            })

    return render(request,'bommanage/success.html')

