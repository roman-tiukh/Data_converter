import zipfile
import xmltodict
import sys, codecs

with zipfile.ZipFile('/home/alex/projects/28-ex_xml_atu (2).zip', 'r') as zip_ref:
    zip_ref.extractall('/home/alex/projects/read_xml')



with codecs.open('28-ex_xml_atu.xml', encoding="cp1251") as file:
    data = xmltodict.parse(file.read()) 

print (data['DATA']['RECORD'][5])

