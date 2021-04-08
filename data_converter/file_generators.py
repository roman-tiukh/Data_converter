import json
from io import StringIO
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework_xml.renderers import XMLRenderer
from abc import ABC, abstractmethod
import lxml.etree as etree


class BaseGenerator(ABC):
    def start(self):
        pass

    @abstractmethod
    def add_list_item(self, data: dict):
        pass

    def finish(self):
        pass

    @abstractmethod
    def get_data(self):
        pass


class XMLGenerator(BaseGenerator):
    def __init__(self, pretty_print: bool = False):
        self.pretty_print = pretty_print
        self.renderer = XMLRenderer()
        self.stream = StringIO()
        self.xml = SimplerXMLGenerator(self.stream, XMLRenderer.charset)

    def start(self):
        self.xml.startDocument()
        self.xml.startElement(XMLRenderer.root_tag_name, {})

    def add_list_item(self, data: dict):
        self.xml.startElement(XMLRenderer.item_tag_name, {})
        self.renderer._to_xml(self.xml, data)
        self.xml.endElement(XMLRenderer.item_tag_name)

    def finish(self):
        self.xml.endElement(XMLRenderer.root_tag_name)
        self.xml.endDocument()

    def get_data(self):
        if not self.pretty_print:
            return self.stream.getvalue()
        else:
            tree = etree.XML(self.stream.getvalue().encode('utf-8'))
            string = etree.tostring(tree, encoding='utf-8', pretty_print=True, xml_declaration=True)
            return string.decode('utf-8')


class JSONGeneratorDict(BaseGenerator):
    def __init__(self, indent: int = None):
        self.indent = indent
        self.items = []

    def add_list_item(self, data: dict):
        self.items.append(data)

    def get_data(self):
        return json.dumps(self.items, ensure_ascii=False, indent=self.indent)


class JSONGenerator(BaseGenerator):
    def __init__(self, indent: int = None):
        self.indent = indent
        self.stream = StringIO()
        self.is_first_item = True

    def dump_json(self, data):
        return json.dumps(data, ensure_ascii=False, indent=self.indent)

    def start(self):
        self.stream.write('[')

    def add_list_item(self, data: dict):
        if self.is_first_item:
            self.is_first_item = False
        else:
            self.stream.write(',')
        self.stream.write(self.dump_json(data))

    def finish(self):
        self.stream.write(']')

    def get_data(self):
        return self.stream.getvalue()
