from django.test import SimpleTestCase

from data_ocean.transliteration.utils import transliterate, translate_company_type_in_string,\
    translate_country_in_string


class TransliterateTestCase(SimpleTestCase):
    def test_translate_country_in_address(self):
        self.assertEqual(
            translate_country_in_string(
                'Україна, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24'
            ),
            'Ukraine, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24'
        )
        self.assertEqual(
            translate_country_in_string(
                'Україна, 32500, Хмельницька обл., Віньковецький р-н, смт. Віньківці, ВУЛИЦЯ СОБОРНА УКРАЇНA'
            ),
            'Ukraine, 32500, Хмельницька обл., Віньковецький р-н, смт. Віньківці, ВУЛИЦЯ СОБОРНА УКРАЇНA'
        )
        self.assertEqual(
            translate_country_in_string(
                'україна, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"'
            ),
            'ukraine, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"'
        )
        self.assertEqual(
            translate_country_in_string(
                '03055, ПРОСПЕКТ ПЕРЕМОГИ, БУД. 15, ЛІТЕРА"А", М. КИЇВ, УКРАЇНА., будинок 15, павільйон ЛІТЕРА"А"'
            ),
            '03055, ПРОСПЕКТ ПЕРЕМОГИ, БУД. 15, ЛІТЕРА"А", М. КИЇВ, UKRAINE., будинок 15, павільйон ЛІТЕРА"А"'
        )

    def test_translate_company_type_in_string(self):
        self.assertEqual(
            translate_company_type_in_string(
                'приватне підприємство "алмаз"'
            ),
            'private enterprise "алмаз"'
        )
        self.assertEqual(
            translate_company_type_in_string(
                'Приватне Підприємство "Алмаз"'
            ),
            'Private Enterprise "Алмаз"'
        )
        self.assertEqual(
            translate_company_type_in_string(
                'Приватне підприємство "Алмаз"'
            ),
            'Private enterprise "Алмаз"'
        )
        self.assertEqual(
            translate_company_type_in_string(
                'ПРИВАТНЕ ПІДПРИЄМСТВО "АЛМАЗ"'
            ),
            'PRIVATE ENTERPRISE "АЛМАЗ"'
        )

    def test_transliterate(self):
        self.assertEqual(
            transliterate(
                'командитне товариство "європейська транспортна група"'
            ),
            'komandytne tovarystvo "yevropeiska transportna hrupa"'
        )
        self.assertEqual(
            transliterate(
                'Споживче Товариство "Яблунівка"'
            ),
            'Spozhyvche Tovarystvo "Yablunivka"'
        )
        self.assertEqual(
            transliterate(
                'ПРИВАТНЕ ПІДПРИЄМСТВО "ЮЛІЯ"'
            ),
            'PRYVATNE PIDPRYIEMSTVO "YULIIA"'
        )

    def test_translate_and_transliterate(self):
        self.assertEqual(
            transliterate(
                translate_country_in_string(
                    'Україна, 42032, ВУЛ. ЖОВТНЕВА, БУД. 71, С. ХРЕЩАТИК, РОМЕНСЬКИЙ РАЙОН, СУМСЬКА ОБЛАСТЬ'
                )
            ),
            'Ukraine, 42032, VUL. ZHOVTNEVA, BUD. 71, S. KHRESHCHATYK, ROMENSKYI RAION, SUMSKA OBLAST'
        )

        self.assertEqual(
            transliterate(
                translate_company_type_in_string(
                    'публічне акціонерне товариство "каховське автотранспортне підприємство 16555"'
                )
            ),
            'public joint-stock company "kakhovske avtotransportne pidpryiemstvo 16555"'
        )
