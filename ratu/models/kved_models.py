from django.db import models

class Section(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
            return self.name

class Division(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
            return self.name

class Group(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
            return self.name

class Kved(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=500)

    def __str__(self):
            return f"КВЕД {self.code}, назва: {self.name}"

    @property
    def empty(self):
        return self.objects.get(code='EMP')
