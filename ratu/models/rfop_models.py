# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Rfop(models.Model):
    fullname = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)
    kved = models.CharField(max_length=250, null=True)
    state = models.CharField(max_length=100, null=True)
