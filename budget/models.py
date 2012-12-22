from django.db import models
from django.contrib import admin

# Create your models here.

class HomologationItem(models.Model):
    CERT_TYPES = (
        ('Anatel','Anatel'),
        ('Audit/Inspection','Audit/Inspection'),
        ('Automotive','Automotive'),
        ('Carrier','Carrier'),
        ('Carrier - AT&T','Carrier - AT&T'),
        ('Carrier - Sprint','Carrier - Sprint'),
        ('Carrier - Verizon','Carrier - Verizon'),
        ('Carrier - Vodafone','Carrier - Vodafone'),
        ('CCC','CCC'),
        ('Country Specific - Anatel','Country Specific - Anatel'),
        ('Country Specific - C-Tick/A-Tick','Country Specific - C-Tick/A-Tick'),
        ('Country Specific - Telec','Country Specific - Telec'),
        ('Emission','Emission'),
        ('Emission/Immunity','Emission/Immunity'),
        ('Environmental','Environmental'),
        ('Immunity','Immunity'),
        ('Intentional Radiator','Intentional Radiator'),
        ('PTCRB','PTCRB'),
        ('Safety','Safety'),
        ('Safety C1D2','Safety C1D2'),
        ('Safety C1D1','Safety C1D1')
    )
    
    CERT_PRESCAN_TYPES = (
        ('',''),
        ('Prescan','Prescan'),
    )
    
    CERT_REGION_TYPES = (
        ('US','US'),
        ('EU','EU'),
        ('Brazil','Brazil'),
        ('China','China'),
        ('India','India'),
        ('Japan','Japan'),
        ('Australia/NZ','Australia/NZ'),
        ('Other','Other'),
    )
    
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=120)
    project_code = models.CharField(max_length=30)
    cert_type = models.CharField(max_length=30, choices=CERT_TYPES)
    cert_prescan = models.CharField(max_length=30, choices=CERT_PRESCAN_TYPES, blank=True)
    region = models.CharField(max_length=30, choices=CERT_REGION_TYPES)
    supplier = models.CharField(max_length=30)
    first_entered = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name + "-" + self.description


class HomologationStatus(models.Model):
    CERT_STATUS = (
        ('New','New'),
        ('Quoting','Quoting'),
        ('Waiting','Waiting'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
        ('In-Progress','In-Progress'),
        ('Completed','Completed'),
        ('Failed','Failed'),
        ('Canceled','Canceled'),
    )
    
    homologation_item = models.ForeignKey(HomologationItem)

    updated = models.DateTimeField()
    update_reason = models.CharField(max_length=50, blank=True)

    status = models.CharField(max_length=30, choices=CERT_STATUS)

    budget_amount = models.IntegerField(blank=True, null=True)
    quoted_amount = models.IntegerField(blank=True, null=True)
    actual_amount = models.IntegerField(blank=True, null=True)

    requested_start = models.DateField()
    ready = models.DateField(blank=True, null=True)    
    started = models.DateField(blank=True, null=True)
    completed = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return str(self.homologation_item) 

class HomologationItemAdmin(admin.ModelAdmin):
    list_display = ['name','description','project_code','cert_type','cert_prescan','region']

admin.site.register(HomologationItem, HomologationItemAdmin)
admin.site.register(HomologationStatus)

