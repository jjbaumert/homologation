# Create your views here.

DIRECTORY_55M = '/mnt/55000000'
DIRECTORY_SEPARATOR = '/'

import os

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
#   move_part(part_number)
#
#--------------------------------------------------------------------
#
#   verify the parts then move them from pending to released
#
#--------------------------------------------------------------------

def move_part(part_number):
    files = get_fileinfo(DIRECTORY_55M+DIRECTORY_SEPARATOR+part_number)

    (_,smallest) = files[0]
    largest = smallest

    for file_info in files:
        (file_name, file_mtime) = file_info

        if largest<file_mtime:
            largest=file_mtime

        if smallest>file_mtime:
            smallest=file_mtime

        print file_mtime, file_name

    print "smallest:", smallest, "largest:", largest, "difference:", (largest-smallest)/60

    print "move part_number", part_number, "to released."


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
            possibilities = form.cleaned_data['possibilities']

            for part_number in possibilities:
                move_part(part_number)

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

        

def success(request):
    return render(request,'bommanage/success.html')
