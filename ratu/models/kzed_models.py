from django.db import models

class Section(models.Model):
    EMPTY_FIELD = 'empty field'
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=150)


class Division(models.Model):
    EMPTY_FIELD = 'empty field'
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)


class Group(models.Model):
    EMPTY_FIELD = 'empty field'
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)

class Kzed(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=1000)
