# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=30, unique=True)

class District(models.Model):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class City(models.Model):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Citydistrict(models.Model):
    EMPTY_FIELD = 'empty field'
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Street(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    citydistrict = models.ForeignKey(Citydistrict, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)