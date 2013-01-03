from django.db import models
from django.contrib import admin

# Create your models here.

class HomologationItem(models.Model):
    CERT_TYPES = (
        ('Audit/Inspection','Audit/Inspection'),
        ('Automotive Electrical','Automotive Electrical'),
        ('Automotive Environmental','Automotive Environmental'),
        ('Carrier','Carrier'),
        ('Carrier - AT&T','Carrier - AT&T'),
        ('Carrier - Sprint','Carrier - Sprint'),
        ('Carrier - Verizon','Carrier - Verizon'),
        ('Carrier - Vodafone','Carrier - Vodafone'),
        ('Carrier - Other','Carrier - Other'),
        ('CCC','CCC'),
        ('SRRC','SRRC'),
        ('Anatel','Anatel'),
        ('Cofetel','Cofetel'),
        ('C-Tick/A-Tick','C-Tick/A-Tick'),
        ('GOST','GOST'),
        ('ISATEL','ISATEL'),
        ('Telec','Telec'),
        ('FCC/CE','FCC/CE'),
        ('FCC/CE/IC','FCC/CE/IC'),
        ('FCC/CE Intentional Radiator','FCC/CE Intentional Radiator'),
        ('Emissions','Emissions'),
        ('Immunity','Immunity'),
        ('Intentional Radiator','Intentional Radiator'),
        ('Environmental','Environmental'),
        ('PTCRB','PTCRB'),
        ('Safety','Safety'),
        ('Safety C1D2','Safety C1D2'),
        ('Safety C1D1','Safety C1D1'),
    )
    
    CERT_PRESCAN_TYPES = (
        ('No','No'),
        ('Yes','Yes'),
    )
    
    CERT_REGION_TYPES = (
        ('US','US'),
        ('EU','EU'),
        ('US/EU','US/EU'),
        ('US/Canada','US/Canada'),
        ('US/EU/Canada','US/EU/Canada'),
        ('Brazil','Brazil'),
        ('Canada','Canada'),
        ('Korea','Korea'),
        ('China','China'),
        ('India','India'),
        ('Japan','Japan'),
        ('Mexico','Mexico'),
        ('Russia','Russia'),
        ('France','France'),
        ('Australia/NZ','Australia/NZ'),
        ('Worldwide','Worldwide'),
        ('Other','Other'),
    )
    
    name = models.CharField(max_length=50, verbose_name='name')
    description = models.CharField(max_length=120, verbose_name='description', blank=True, null=True)
    project_code = models.CharField(max_length=30, verbose_name='project code')
    cert_type = models.CharField(max_length=30, verbose_name='certification', choices=CERT_TYPES)
    cert_prescan = models.CharField(max_length=30, verbose_name='prescan', choices=CERT_PRESCAN_TYPES, blank=True)
    region = models.CharField(max_length=30, verbose_name='region', choices=CERT_REGION_TYPES)
    module = models.CharField(max_length=30, verbose_name='module', blank=True)
    supplier = models.CharField(max_length=30, verbose_name='supplier')
    first_entered = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name + "-" + self.description

class HomologationStatus(models.Model):
        
    CERT_APPROVAL_STATUS = (
        ('Requested','Requested'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
        ('Deferred','Deferred'),
    )

    CERT_STATUS = (
        ('Quoting','Quoting'),
        ('Ready','Ready'),
        ('In-Progress','In-Progress'),
        ('Passed','Passed'),
        ('Failed','Failed'),
        ('Completed','Completed'),
        ('Canceled','Canceled'),
    )
    
    homologation_item = models.ForeignKey(HomologationItem)
    active_record = models.BooleanField()

    updated = models.DateTimeField()
    update_reason = models.CharField(max_length=300, blank=True)

    approval_status = models.CharField(max_length=30, choices=CERT_APPROVAL_STATUS)
    certification_status = models.CharField(max_length=30, choices=CERT_STATUS)
    
    budget_amount = models.IntegerField(blank=True, null=True)
    quoted_amount = models.IntegerField(blank=True, null=True)
    actual_amount = models.IntegerField(blank=True, null=True)

    requested_start = models.DateField()
    ready = models.DateField(blank=True, null=True)    
    approved_for = models.DateField(blank=True, null=True)    
    started = models.DateField(blank=True, null=True)
    completed = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return str(self.homologation_item) 

class HomologationItemAdmin(admin.ModelAdmin):
    list_display = ['name','description','project_code','cert_type','cert_prescan','region']

admin.site.register(HomologationItem, HomologationItemAdmin)
admin.site.register(HomologationStatus)

