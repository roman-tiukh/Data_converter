from django.db import models
from ratu.models.ruo_models import Kved

class Staterfop(models.Model):
    EMPTY_FIELD = 'empty field'
    name = models.CharField(max_length=100, unique=True, null=True)

class Rfop(models.Model): 
    state = models.ForeignKey(Staterfop, on_delete=models.CASCADE)
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)