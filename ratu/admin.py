from django.contrib import admin
import xmltodict
import sys, codecs
# Register your models here.
from .models import Choice, Question
from .models import Region
# from django.utils import timezone
Question.objects.all().delete()

with codecs.open('/home/ivan/Project/Django/data_converter/ratu_test.xml', encoding="cp1251") as file:
    data = xmltodict.parse(file.read()) 

print (data['DATA']['RECORD'][10])


for x in data['DATA']:

    region = Region(name=x['OBL_NAME'])
   # region.name = 
    region.save()


q = Question(question_text="What view?")
# delete
q.save()
print(q.question_text)
print(q.id)

