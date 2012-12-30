#!/usr/bin/python
import sys
from django.core.management import setup_environ
from homologation import settings

setup_environ(settings)

from budget.models import HomologationItem

HomologationItem.objects.all().delete()

sys.path.append('./budget/data/')
import parse_homologation

