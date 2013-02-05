from django.db import models

# Create your models here.

class BomLog(models.Model):
    REVIEW_STATUS = (
        ('passed', 'passed'),
        ('failed', 'failed'),
    )

    part_number    = models.CharField(max_length=20)
    part_variant   = models.CharField(max_length=5)
    revision       = models.CharField(max_length=10)

    user           = models.CharField(max_length=30)
    review_date    = models.DateTimeField()
    review_status  = models.CharField(max_length=30)
    review_results = models.CharField(max_length=1000)
    review_notes   = models.CharField(max_length=1000)


class BomFileLog(models.Model):
    bom_log        = models.ForeignKey(BomLog)

    file_path      = models.CharField(max_length=100)
    file_name      = models.CharField(max_length=100)
    file_date      = models.DateTimeField()


