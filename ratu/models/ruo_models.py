# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=500, null=True)
    short_name = models.CharField(max_length=500, null=True)
    edrpou = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    boss = models.CharField(max_length=250, null=True)
    kved = models.CharField(max_length=500, null=True)
    state = models.CharField(max_length=500, null=True)

class Founders(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    founder = models.TextField(null=True)