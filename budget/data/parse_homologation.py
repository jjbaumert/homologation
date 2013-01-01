#!/usr/bin/python

from django.core.management import setup_environ
from homologation import settings

setup_environ(settings)

import csv
import re
import datetime

now = datetime.datetime.now()

from budget.models import HomologationItem, HomologationStatus

re_fyq=re.compile("FY([0-9]{2})-Q([0-9])")

data = csv.reader(open('/home/kender/project/homologation/budget/data/Homologation.csv'))

fields = data.next()

homologation_list = []

HomologationItem.objects.all().delete()

for row in data:
    row_map = {}
    
    for x in range(0,len(fields)):
        row_map[fields[x]] = row[x]
        
    homologation_list.append(row_map)


cert_approval_status = {
        'Requested':'Requested',
        'Approved':'Approved',
        'Completed':'Approved',
        'Rejected':'Rejected',
        'Cancelled':'Cancelled',
}

cert_status = {
        'Quoting':'Quoting',
        'Ready':'Ready',
        'Submitting':'Submitting',
        'Not started':'Submitting',
        'In-Progress':'In-Progress',
        'In Progress':'In-Progress',
        'In progress':'In-Progress',
        'Passed':'Passed',
        'Failing':'Failing',
        'Failed':'Failed',
        'Completed':'Completed',
        'Complete':'Completed',
        'Reviewing':'Completed',
        'Report':'Completed',
        'Canceled':'Canceled',
}

cert=  {'Audit/Inspection':'Audit/Inspection',
        'Automotive: Electrical':'Automotive Electrical',
        'Automotive: Environmental':'Automotive Environmental',
        'Carrier':'Carrier',
        'Carrier Certification':'Carrier',
        'Carrier - AT&T':'Carrier - AT&T',
        'Carrier - Sprint':'Carrier - Sprint',
        'Carrier - Verizon':'Carrier - Verizon',
        'Carrier - Vodafone':'Carrier - Vodafone',
        'Carrier - Other':'Carrier - Other',
        'CCC':'CCC',
        'GOST':'GOST',
        'GOST R':'GOST',
        'ISATEL':'ISATEL',
        'China CCC':'CCC',
        'China SRRC':'SRRC',
        'Anatel':'Anatel',
        'Cofetel':'Cofetel',
        'C-Tick/A-Tick':'C-Tick/A-Tick',
        'C-Tick':'C-Tick/A-Tick',
        'Telec':'Telec',
        'FCC/CE':'FCC/CE',
        'FCC/CE: Emissions':'FCC/CE',
        'FCC/CE: EMI':'FCC/CE',
        'FCC/CE: Intentional Radiator':'FCC/CE Intentional Radiator',
	'Emissions':'Emissions',
	'Immunity':'Immunity',
	'EMC':'Emissions',
	'Country EMI':'Emissions',
	'Prescan EMI':'Emissions',
	'Country Intentional Radiator':'Intentional Radiator',
        'Environmental':'Environmental',
        'PTCRB':'PTCRB',
        'Prescan PTCRB':'PTCRB',
        'Safety':'Safety',
        'Safety C1D2':'Safety C1D2',
        'Safety C1D1':'Safety C1D1',
	'Factory Inspection':'Audit/Inspection'}

region = {'US':'US',
        'EU':'EU',
        'Europe':'EU',
        'Brazil':'Brazil',
        'China':'China',
        'India':'India',
        'Japan':'Japan',
        'ANZ':'Australia/NZ',
        'Australia/NZ':'Australia/NZ',
        'Australia':'Australia/NZ',
        'Australia/New Zealand':'Australia/NZ',
        'All':'Worldwide',
        'Worldwide':'Worldwide',
	'Mexico':'Mexico',
	'Russia':'Russia',
	'Korea':'Korea',
        'All':'Worldwide',
	'US, Thailand, Indonesia':'Other',
	'':'Other',
        'Global':'Worldwide',
        'Other':'Other',
        'US/EU':'US/EU',
        'USA AND EU':'US/EU',
        'US/EU/Canada':'US/EU/Canada',
        'Canada/EU/USA':'US/EU/Canada',
        'US/Can/EU':'US/EU/Canada',
        'USA/Can/EU':'US/EU/Canada',
        'USA/CAN/EU':'US/EU/Canada',
        'NA and EU':'US/EU/Canada',
        'USA/IC/EU':'US/EU/Canada',
        'EU, USA, Canada':'US/EU/Canada',
        'US/CAN/EU':'US/EU/Canada',
        'US/IC/EU':'US/EU/Canada',
        'US and EU':'US/EU',
        'USA/EU':'US/EU',
	'ETSI EN 300 220, ETSI EN 301 489-3, EN 62311, ETSI EN 60950':'EU',
        'USA and EU':'US/EU',
        'US/Canada':'US/Canada',
        'Canada/US':'US/Canada',
        'USA/Can':'US/Canada',
        'US and Canada':'US/Canada',
        'US/Can':'US/Canada',
        'USA/CAN':'US/Canada',
        'USA/IC':'US/Canada',
	'Canada':'Canada',
	'France':'France',
	'North America': 'US/Canada',
	'NOrth America': 'US/Canada',
	'NA': 'US/Canada',
	'USA':'US',
	'United States':'US'}
    
for item in homologation_list:
    if item['Title']=='TCFs':
        continue

    if item['Title']=='GOST R':
	item['Region']='Russia'
	item['Cert Type']='GOST'

    if item['Title'][:3]=='ALT':
	item['Cert Type']='Envorinmental'

    if item['Region']=='Brazil':
	item['Cert Type']='Anatel'

    if item['Region']=='EU and NA':
	item['Cert Type']='FCC/CE'
	item['Region']='US/EU'

    if item['Region']=='Mexico':
	item['Cert Type']='Cofetel'

    if item['Title']=='M100':
	item['Cert Type']='Carrier - Other'

    if item['Cert Type']=='Country Other' and item['Region']=='China':
	item['Cert Type']='CCC'

    if item['Title']=='C-Tick Conversion':
	item['Cert Type']='C-Tick/A-Tick'

    if item['Cert Type']=='Country Other' and item['Region']=='Australia' or item['Region']=='Australia/NZ' or item['Region']=='Australia/New Zealand':
	item['Cert Type']='C-Tick/A-Tick'

    if item['Region']=='Japan':
	item['Cert Type']='Telec'

    if item['Cert Type']=='Country Other' and item['Region']=='Japan':
	item['Cert Type']='Telec'

    if item['Cert Type']=='Country Other' and item['Region']=='Russia':
	item['Cert Type']='GOST'

    if item['Title']=='Factory Inspection' or item['Title']=='Annual Fee':
	item['Cert Type']='Audit/Inspection'

    if item['Supplier']=='Environ Lab':
	item['Cert Type']='Environmental'

    if item['Supplier']=='Braco':
	item['Cert Type']='C-Tick/A-Tick'
	item['Region']='Australia/NZ'

    if item['Supplier']=='G&M Compliance':
	item['Cert Type']='CCC'
	item['Region']='China'

    if item['Supplier']=='MET':
	item['Cert Type']='Safety'

    if item['Cert Type']=='FCC/CE':
        item['Region']='US/EU'

   #
   # Reject remaining records that are not correct
   #

    if not cert.__contains__(item['Cert Type']):
	print "%s for Cert Type: \"%s\" rejected." % (item['Title'],item['Cert Type'])
	continue
    else:
        item['Cert Type'] = cert[item['Cert Type']]

    if not region.__contains__(item['Region']):
    	print "%s for Region: \"%s\" rejected." % (item['Title'],item['Region'])
	continue
    else:
        item['Region'] = region[item['Region']]
        
    if not cert_approval_status.__contains__(item['BT Status']):
    	print "%s for Approval: \"%s\" rejected." % (item['Title'],item['BT Status'])
        continue
    else:
        item['BT Status'] = cert_approval_status[item['BT Status']]
        

    if not cert_status.__contains__(item['CT Status']):
    	print "%s for Cert Status: \"%s\" rejected." % (item['Title'],item['CT Status'])
	continue
    else:
        item['CT Status'] = cert_status[item['CT Status']]

    if item['Budget']=='':
        item['Budget']=item['Request']

    if item['Request']=='':
        item['Request']=item['Budget']

    if item['Paid']=="":
	item['Paid']=item['Budget']

    result = re_fyq.match(item['BQ'])
    if not result:
    	print "%s rejected for bad quarter" % (item['title'],item['BQ'])
	continue

    (year,quarter) = (int(result.group(1)),int(result.group(2)))

    #print "#### ", item['BQ'], "-", 2000+int(year), year, quarter

    if quarter==1:
        monthday='-10-01'
	year=year-1
    elif quarter==2:
        monthday='-01-01'
    elif quarter==3:
        monthday='-04-01'
    elif quarter==4:
        monthday='-07-01'
    else:
        print "%s rejected for bad quarter %s" % (item['title'],item['BQ'])
	continue

    year = int(year) + 2000

    item['BQ'] = str(year)+monthday

    completed=""
    if item['CT Status']=='Completed':
       completed = item['BQ']
        
    """
    ['Project Code', 'Title', 'BQ', 'Supplier', 'CT Status', 'Remaining', 'Request Start', 'CID', 'Accrual', 'Paid', 'ID', 'Cellular Modul
e', 'Date', 'Path', 'PO', 'Region', 'Request', 'Budget', 'Modified', 'Dept', 'Cert Type', 'BT Status', 'Certification', 'Item Type', '
Invoice']
    """
    print item

    print "name="+item['Title']
    print "description="+" "
    print "project_code="+item['Project Code']
    print "cert_type="+item['Cert Type']
    print "cert_prescan="
    print "region="+item['Region']
    print "supplier="+item['Supplier']
    print "module="+item['Cellular Module']
    print "update=Historical Entry"
    print "updated=2012-26-12"
    print "approval_status="+item['BT Status']
    print "certification_status="+item['CT Status']
    print "budget_amount="+item['Budget']
    print "quoted_amount="+item['Request']
    print "actual_amount="+item['Paid']
    print "approved_for="+item['BQ']
    print "completed="+completed
    print "department="+item['Dept']
    print "\r\n"
    
    p = HomologationItem()
    s = HomologationStatus()
    
    p.name = item['Title']
    p.description = ' '
    p.project_code = item['Project Code']
    p.cert_type = item['Cert Type']
    p.region = item['Region']
    p.module = item['Cellular Module']
    p.supplier = item['Supplier']

    s.active_record = True
    s.approval_status = item['BT Status']
    s.certification_status = item['CT Status']
    
    if item['Budget']!='':
        s.budget_amount = int(float(item['Budget']))
    
    if item['Request']!='':
        s.quoted_amount = int(float(item['Request']))
    
    if item['Paid']!='':
        s.actual_amount = int(float(item['Paid']))
    
    s.requested_start = item['BQ']

    if s.approval_status=='Approved' or s.approval_status=='Complete':
        s.approved_for = item['BQ']
    s.updated = now
    s.update_reason = 'Initial Creation'
    
    p.save()
    s.homologation_item=p
    s.save()
