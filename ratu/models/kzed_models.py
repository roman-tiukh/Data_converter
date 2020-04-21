from django.db import models

class Section(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=150)


    def __str__(self):
            return self.name


class Division(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)


    def __str__(self):
            return self.name


class Group(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self):
            return self.name


class Kzed(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=1000)

    def __str__(self):
            return self.name

