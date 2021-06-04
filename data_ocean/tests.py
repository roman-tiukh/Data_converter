import random
import re

from django.test import SimpleTestCase
# from django.test.runner import DiscoverRunner

# from business_register.models.company_models import Company
from data_ocean.transliteration.utils import transliterate, translate_company_type_in_string,\
    translate_country_in_string


# class NoDbTestRunner(DiscoverRunner):
#     """ A test runner to test without database creation """
#
#     def setup_databases(self, **kwargs):
#         """ Override the database creation defined in parent class """
#         pass
#
#     def teardown_databases(self, old_config, **kwargs):
#         """ Override the database teardown defined in parent class """
#         pass


class TransliterateTestCase(SimpleTestCase):
    # def setUp(self):
    #     company_ids = list(Company.objects.values('id'))
    #     company_id = random.sample(company_ids, 1)[0]['id']
    #     self.testing_company = Company.objects.get(id=company_id)

    def test_translate_country_in_address(self):
        self.assertEqual(
            translate_country_in_string(
                'Україна, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24'
            ),
            'Ukraine, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24'
        )
        self.assertEqual(
            translate_country_in_string(
                'Україна, 94407, ПЛ.ЛЕНІНА, 6, ГОТЕЛЬ УКРАЇНА, М.КРАСНОДОН, ЛУГАНСЬКА ОБЛАСТЬ'
            ),
            'Ukraine, 94407, ПЛ.ЛЕНІНА, 6, ГОТЕЛЬ УКРАЇНА, М.КРАСНОДОН, ЛУГАНСЬКА ОБЛАСТЬ'
        )
        self.assertEqual(
            translate_country_in_string(
                'Україна, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"'
            ),
            'Ukraine, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"'
        )

