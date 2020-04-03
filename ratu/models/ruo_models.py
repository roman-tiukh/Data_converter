# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

class State_Ruo(models.Model):

    EMPTY_FIELD = 'empty field'
    name = models.CharField(max_length=100, unique=True, null=True)

class Ruo(models.Model):

    state = models.ForeignKey(State_Ruo, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=True)
    short_name = models.CharField(max_length=500, null=True)
    edrpou = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    boss = models.CharField(max_length=250, null=True)
    kved = models.CharField(max_length=500, null=True)

class Founders(models.Model):

    company = models.ForeignKey(Ruo, on_delete=models.CASCADE)
    founder = models.TextField(null=True)