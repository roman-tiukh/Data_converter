from lxml import etree

from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):
    help = 'getting records from source files by tags values'

    def add_arguments(self, parser):
        parser.add_argument('search_text', nargs='?')
        parser.add_argument('tag', default='EDRPOU', nargs='?')
        parser.add_argument('source', choices=['uo', 'fop', 'uos', 'fops', 'ratu'], default='uo', nargs='?')

    def print_recursion(self, record, root_tab):
        for elem in record:
            print(root_tab, elem.tag, ':', elem.text or '')
            child_tab = root_tab + '\t'
            self.print_recursion(elem, child_tab)

    def handle(self, *args, **options):
        converter_module = ('business_register.converter.company_converters.ukr_company_full.UkrCompanyFullConverter'
                            if options['source'] == 'uo' else
                            'business_register.converter.fop.FopConverter' if options['source'] == 'fop' else
                            'business_register.converter.company_converters.ukr_company.UkrCompanyConverter'
                            if options['source'] == 'uos' else
                            'location_register.converter.ratu.RatuConverter' if options['source'] == 'ratu' else
                            options['source'])
        converter = import_string(converter_module)()
        elements = etree.iterparse(
            source=converter.LOCAL_FOLDER + converter.LOCAL_FILE_NAME,
            tag=converter.RECORD_TAG,
            recover=False,
        )
        index = 0
        for _, record in elements:
            index += 1
            text_from_record = record.xpath(options['tag'])[0].text
            if text_from_record == options['search_text']:
                print('Record #', index, 'from:', converter.LOCAL_FILE_NAME)
                print('-------------------------------------------------------------------------')
                self.print_recursion(record, '')
                print('-------------------------------------------------------------------------')
            record.clear()
            for ancestor in record.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
