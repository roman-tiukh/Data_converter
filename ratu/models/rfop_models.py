# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class State_Rfop(models.Model):

    EMPTY_FIELD = 'empty field'
    name = models.CharField(max_length=100, unique=True, null=True)

class Rfop(models.Model):
    
    state = models.ForeignKey(State_Rfop, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)
    kved = models.CharField(max_length=250, null=True)