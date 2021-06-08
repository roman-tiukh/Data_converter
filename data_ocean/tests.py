from django.test import SimpleTestCase

from data_ocean.transliteration.utils import transliterate, translate_company_type_in_string,\
    translate_country_in_string


class TransliterateTestCase(SimpleTestCase):
    def test_translate_country_in_address(self):
        variants = (
            (
                'Україна, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24',
                'Ukraine, 36014, Полтавська обл., місто Полтава, ПЛОЩА ПАВЛЕНКІВСЬКА, будинок 24'
            ),
            (
                'Україна, 32500, Хмельницька обл., Віньковецький р-н, смт. Віньківці, ВУЛИЦЯ СОБОРНА УКРАЇНA',
                'Ukraine, 32500, Хмельницька обл., Віньковецький р-н, смт. Віньківці, ВУЛИЦЯ СОБОРНА УКРАЇНA'
            ),
            (
                'україна, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"',
                'ukraine, 08606, Київська обл., Васильківський р-н, село Крушинка, ТЕРИТОРІЯ ПТАХОФАБРИКИ "УКРАЇНА"'
            ),
            (
                '03055, ПРОСПЕКТ ПЕРЕМОГИ, БУД. 15, ЛІТЕРА"А", М. КИЇВ, УКРАЇНА., будинок 15, павільйон ЛІТЕРА"А"',
                '03055, ПРОСПЕКТ ПЕРЕМОГИ, БУД. 15, ЛІТЕРА"А", М. КИЇВ, UKRAINE., будинок 15, павільйон ЛІТЕРА"А"'
            ),
        )
        for tested, expected in variants:
            self.assertEqual(translate_country_in_string(tested), expected)

    def test_translate_company_type_in_string(self):
        variants = (
            (
                'приватне підприємство "алмаз"',
                'private enterprise "алмаз"'
            ),
            (
                'Приватне Підприємство "Алмаз"',
                'Private Enterprise "Алмаз"'
            ),
            (
                'Приватне підприємство "Алмаз"',
                'Private enterprise "Алмаз"'
            ),
            (
                'ПРИВАТНЕ ПІДПРИЄМСТВО "АЛМАЗ"',
                'PRIVATE ENTERPRISE "АЛМАЗ"'
            )
        )
        for tested, expected in variants:
            self.assertEqual(translate_company_type_in_string(tested), expected)

    def test_transliterate(self):
        variants = (
            (
                'командитне товариство "європейська транспортна група"',
                'komandytne tovarystvo "yevropeiska transportna hrupa"'
            ),
            (
                'Споживче Товариство "Яблунівка"',
                'Spozhyvche Tovarystvo "Yablunivka"'
            ),
            (
                'ПРИВАТНЕ ПІДПРИЄМСТВО "ЮЛІЯ"',
                'PRYVATNE PIDPRYIEMSTVO "YULIIA"'
            )
        )
        for tested, expected in variants:
            self.assertEqual(transliterate(tested), expected)

    def test_translate_country_and_transliterate(self):
        variants = (
            (
                'Україна, 42032, ВУЛ. ЖОВТНЕВА, БУД. 71, С. ХРЕЩАТИК, РОМЕНСЬКИЙ РАЙОН, СУМСЬКА ОБЛАСТЬ',
                'Ukraine, 42032, VUL. ZHOVTNEVA, BUD. 71, S. KHRESHCHATYK, ROMENSKYI RAION, SUMSKA OBLAST'
            ),
            (
                'Україна, 55000, Миколаївська обл., місто Южноукраїнськ, ПРОМИСЛОВИЙ МАЙДАНЧИК, 13 А',
                'Ukraine, 55000, Mykolaivska obl., misto Yuzhnoukrainsk, PROMYSLOVYI MAIDANCHYK, 13 A'
            )
        )
        for tested, expected in variants:
            self.assertEqual(transliterate(translate_country_in_string(tested)), expected)

    def test_translate_company_type_and_transliterate(self):
        variants = (
            (
                'спільне підприємство "новоодеське заготівельно-переробне торгове підприємство"',
                'joint enterprise "novoodeske zahotivelno-pererobne torhove pidpryiemstvo"'
            ),
            (
                'публічне акціонерне товариство "каховське автотранспортне підприємство 16555"',
                'public joint-stock company "kakhovske avtotransportne pidpryiemstvo 16555"'
            ),
            (
                'товариство з обмеженою відповідальністю "український кур\'єр"',
                'limited trade development "ukrainskyi kurier"'
            ),
            (
                'товариство з обмеженою відповідальністю "український кур`єр"',
                'limited trade development "ukrainskyi kurier"'
            ),
            (
                'товариство з обмеженою відповідальністю "український кур’єр"',
                'limited trade development "ukrainskyi kurier"'
            )
        )
        for tested, expected in variants:
            self.assertEqual(transliterate(translate_company_type_in_string(tested)), expected)
