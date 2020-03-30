
import codecs
import xmltodict
import xml.etree.ElementTree
from xml.etree.ElementTree import iterparse, XMLParser, tostring


# tree = xml.etree.ElementTree.parse('/home/ivan/Project/Django/17.1-EX_XML_EDR_UO_26.03.2020.xml')
# root = tree.getroot()

# print(root.tag)

i=0
record = {
    'RECORD': [],
    'NAME': [],
    'SHORT_NAME': [],
    'EDRPOU': [],
    'ADDRESS': [],
    'BOSS': [],
    'KVED': [],
    'STAN': [],
    'FOUNDING_DOCUMENT_NUM': [],
    'FOUNDERS': [],
    'FOUNDER': []
}

#     'RECORD': [],
#     'FIO': [],
#     'ADDRESS': [],
#     'KVED': [],
#     'STAN': []
# }
#     'RECORD': '',
#     'OBL_NAME': '',
#     'REGION_NAME': '',
#     'CITY_NAME': '',
#     'CITY_REGION_NAME': '',
#     'STREET_NAME': ''
# }
# 
# /home/ivan/Project/Django/Data_convertor/unzipped_xml/28-ex_xml_atu.xml
# /home/ivan/Project/Django/17.1-EX_XML_EDR_UO_26.03.2020.xml


# context = iterparse("/home/ivan/Project/Django/17.2-EX_XML_EDR_FOP_26.03.2020.xml")

# for event, elem in context:
#     if elem.tag == "RECORD":
#         i=i+1
#         print(i,'\n\n................................................................................................')
#         for text in elem.iter():
#             print(text.tag, text.text)
#             record[text.tag].append(text.text)
#             # if not text.tag in record:
#             #     record[text.tag]=[text.text]
#             # else:
#             #     record[text.tag].append(text.text)
#         print(record)
#         for key in record:
#             record[key].clear() 

#         elem.clear()

# with codecs.open("/home/ivan/Project/Django/17.1-EX_XML_EDR_UO_26.03.2020.xml", "r", encoding="cp1251") as file:
    
#     #if f.mode == 'r':
#     #   contents =f.read()
#     #    print (contents)
#     #or, readlines reads the individual line into a list
#     fl=file.readlines(100)
#     for x in fl:
#         print(x)
#     file.close()

# get an iterable
# i=0
context = iterparse("/home/ivan/Project/Django/17.1-EX_XML_EDR_UO_26.03.2020.xml", events=("start", "end"))

# turn it into an iterator
context = iter(context)

# get the root element
event, root = context.__next__()

for event, elem in context:
    if event == "end" and elem.tag == "RECORD":
       
        i=i+1
        print(i, '\n')
        print('................................................................................................')
        for text in elem.iter():
            print(text.tag, text.text)
            record[text.tag].append(text.text)
            # if not text.tag in record:
            #     record[text.tag]=[text.text]
            # else:
            #     record[text.tag].append(text.text)
        print(record)
        for key in record:
            record[key].clear()      
        
        
        # for text in elem.iter('RECORD'):

        #     print([text.tag for text in elem.iter()])
        #     print(tostring(text, encoding='utf8').decode('utf8'))
        root.clear()
