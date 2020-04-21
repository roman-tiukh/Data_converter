from django.db import models
from ratu.models.kzed_models import Kzed 

class Kved(models.Model):
    EMPTY_FIELD = 'empty field'
    name = models.CharField(max_length=500, unique=True, null=True)

    def __str__(self):
            return self.name

class State(models.Model):
    EMPTY_FIELD = 'empty field'
    name = models.CharField(max_length=100, unique=True, null=True)
    
    def __str__(self):
            return self.name

class Ruo(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=True)
    short_name = models.CharField(max_length=500, null=True)
    edrpou = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    boss = models.CharField(max_length=250, null=True)

    def __str__(self):
            return self.name
    
class Founders(models.Model):
    company = models.ForeignKey(Ruo, on_delete=models.CASCADE)
    founder = models.TextField(null=True)