from django.db import models

class Section(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)


class Division(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)


class Group(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

#@toDo unite with other Models
# class Kzed(models.Model):
#     section = models.ForeignKey(Section, on_delete=models.CASCADE)
#     division = models.ForeignKey(Division, on_delete=models.CASCADE)
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     code = models.CharField(max_length=10, unique=True)
#     name = models.CharField(max_length=100)
