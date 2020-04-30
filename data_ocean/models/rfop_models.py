from django.db import models
from data_ocean.models.ruo_models import State
from data_ocean.models.kved_models import Kved

class Rfop(models.Model): 
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    kved = models.ForeignKey(Kved, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)

    def __str__(self):
                return self.fullname
