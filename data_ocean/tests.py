import random
import re

from django.test import TestCase
from django.test.runner import DiscoverRunner

from business_register.models.company_models import Company
from data_ocean.utils import transliterate_field, ukr_to_en


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation """

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class """
        pass


class TransliterateTestCase(TestCase):
    def setUp(self):
        company_ids = list(Company.objects.values('id'))
        company_id = random.sample(company_ids, 1)[0]['id']
        self.testing_company = Company.objects.get(id=company_id)

    def test_is_ukr_chars_in_string(self):
        company_name = transliterate_field(self.testing_company.name, 'company_name')
        address = transliterate_field(self.testing_company.address, 'address')
        if re.search("[А-ЩЬЮЯҐЄІЇа-щьюяґєії]", company_name):
            company_name = None
        if re.search("[А-ЩЬЮЯҐЄІЇа-щьюяґєії]", address):
            address = None
        print(company_name)
        print(address)
        self.assertEqual(transliterate_field(self.testing_company.name, 'company_name'), company_name)
        self.assertEqual(transliterate_field(self.testing_company.address, 'address'), address)
