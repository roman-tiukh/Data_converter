from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import CompanyType
from business_register.emails import send_new_company_type_message


class CompanyConverter(BusinessConverter):
    def __init__(self):
        self.COMPANY_TYPES_UK_EN = {
            'інші організаційно-правові форми': 'other company type',
            'товариство з обмеженою відповідальністю': 'limited trade development',
            'виробничий кооператив': 'industrial cooperative',
            'дочірнє підприємство': 'subsidiary undertaking',
            'державна організація (установа, заклад)':
                'state organization (enterprise, institution)',
            'приватне підприємство': 'private enterprise',
            'релігійна організація': 'religious organization',
            'закрите акціонерне товариство': 'private company limited by shares',
            'державне підприємство': 'state owned enterprise',
            'відкрите акціонерне товариство': 'open joint stock market entity',
            'громадська організація': 'non-governmental organization',
            'обслуговуючий кооператив': 'service cooperative',
            'колективне підприємство': 'employee-owned enterprise',
            'комунальне підприємство': 'municipal enterprise',
            'комунальна організація (установа, заклад)':
                'municipal organization (enterprise, institution)',
            'політична партія': 'political party',
            'підприємство споживчої кооперації': 'consumers cooperative society',
            'орган місцевого самоврядування': 'local government institution',
            'благодійна організація': 'charitable organization',
            'корпорація': 'corporation',
            'іноземне підприємство': 'foreign enterprise',
            'спільне підприємство': 'joint enterprise',
            'асоціація': 'association',
            'орган державної влади': 'public authority',
            'споживче товариство': 'consumer company',
            'фермерське господарство': 'farm enterprise',
            'орган виконавчої влади': 'government authority',
            'сільськогосподарський виробничий кооператив': 'agricultural production cooperative',
            'орган самоорганізації населення': 'community council',
            'повне товариство': 'unlimited partnership',
            'сільськогосподарський обслуговуючий кооператив': 'agricultural service cooperative',
            "об'єднання співвласників багатоквартирного будинку":
                'association of co-owners of apartment house',
            'профспілка': 'trade union',
            'кооперативи': 'cooperatives',
            'селянське (фермерське) господарство': 'farm',
            "організація (установа, заклад) об'єднання громадян":
                'citizens organization (enterprise, institution)',
            "підприємство об'єднання громадян (релігійної організації,профспілки)":
                'citizens enterprise association (religious organization, trade unions)',
            'приватна організація (установа, заклад)':
                'private organization (enterprise, institution)',
            "інші об'єднання юридичних осіб": 'other associations of legal entities',
            'товарна біржа': 'commodity exchange',
            'товариство з додатковою відповідальністю': 'superadded liability company',
            'орендне підприємство': 'rental company',
            'кредитна спілка': 'credit union',
            'акціонерне товариство': 'joint stock company',
            'спілка споживчих товариств': 'community of consumer cooperatives',
            "об'єднання громадян, профспілки, благодійні організації та інші подібні організації":
                'citizens` associations, trade unions, charitable and other organizations',
            'командитне товариство': 'limited partnership',
            'організація роботодавців': "employers' organisation",
            'концерн': 'concern',
            'відокремлені підрозділи без статусу юридичної особи': 'branches',
            'споживчий кооператив': 'consumer cooperative',
            'організації (установи, заклади)': 'organizations (enterprises, institutions)',
            'підприємства': 'enterprises',
            "об'єднання підприємств (юридичних осіб)": 'association of enterprises',
            'консорціум': 'consortium',
            "спілка об'єднань громадян": 'union of associations of citizens',
            "філія (інший відокремлений підрозділ)": 'branch (separate unit)',
            'організація орендарів': 'organization of tenants',
            'недержавний пенсійний фонд': 'private pension fund',
            'державна акціонерна компанія (товариство)': 'state-controlled joint-stock company',
            'господарські товариства': 'business partnership',
            'представництво': 'agency',
            "об'єднання профспілок": 'trade union association',
            'гаражний кооператив': 'garage cooperative',
            'приватне акціонерне товариство': 'private joint-stock company',
            'садівниче товариство': 'gardeners partnership',
            'публічне акціонерне товариство': 'public joint-stock company',
            'творча спілка (інша професійна організація)':
                'creative union (professional organization)',
            'житлово-будівельний кооператив': 'house construction cooperative',
            'казенне підприємство': 'state-run enterprise',
            'сімейне підприємство': 'family enterprise',
            'організація покупців': 'consumers association',
            'підприємець-фізична особа': 'private entrepreneur',
            'індивідуальне підприємство': 'sole proprietorship',
            'органи адвокатського самоврядування': "lawyers` self-government body",
            'холдингова компанія': 'holding company',
            "адвокатське об'єднання": "lawyers` union",
            'адвокатське бюро': 'law firm',
            'судова система': 'judiciary',
            "асоціації органів місцевого самоврядування та їх добровільні обєднання":
                'associations of local government bodies and their voluntary associations',
            'кооперативний банк': 'cooperative bank',
            'аудиторська палата україни': 'the auditors chamber of ukraine',
            'приватна компанія з обмеженою відповідальністю': 'private limited company',
            'благодійне товариство': 'charitable incorporated organisation',
            'приватна компанія з відповідальністю, обмеженою гарантіями її членів':
                'pri/ltd by guar/nsc (private, limited by guarantee, no share capital)',
            'компанія суспільних інтересів': 'community interest company',
            'зареєстроване товариство': 'registered society',
            'обмежене партнерство': 'limited partnership',
            'королівська статутна компанія': 'royal charter company',
            'партнерство з обмеженою відповідальністю': 'limited liability partnership',
            ("приватна компанія з відповідальністю, обмеженою гарантіями її членів з використанням 'обмеженої' пільги"):
                ("pri/lbg/nsc (private, limited by guarantee, no share capital, use of 'limited' exemption)"),
            'шотландське благодійне товариство': 'scottish charitable incorporated organisation',
            'приватна компанія з необмеженою відповідальністю': 'private unlimited company',
            'давно існуюча публічна компанія': 'old public company',
            'товариство': 'private unlimited',
            'шотландське партнерство': 'scottish partnership',
            'інвестиційна компанія зі змінним капіталом (цінні папери)':
                'investment company with variable capital (securities)',
            'інвестиційна компанія зі змінним капіталом':
                'investment company with variable capital',
            'промислове товариство взаємного кредиту': 'industrial and provident society',
            "інвестиційна компанія зі змінним капіталом ('парасолькова компанія')":
                'investment company with variable capital(umbrella)',
            ('приватна компанія з обмеженою відповідальністю згідно підрозділу 30 закону'
             ' о компаніях'):
                'priv ltd sect. 30 (private limited company, section 30 of the companies act)',
            'європейське публічне товариство з обмеженою відповідальністю':
                "european public limited-liability company (se)",
            'перероблена/закрита': 'converted/closed',
            'компанія з розділеними портфелями': 'protected cell company',
            'публічна акціонерна компанія з обмеженою відповідальністю': 'public limited company',
            'додаткова освіта та передуніверситетський коледж/коледжний корпус':
                'further education and sixth form college corps',
            'приватна/компанія з відповідальністю, обмеженою гарантіями її членів/без акціонерного капіталу, використання "обмеженої" пільги (або привілегії)':
                "pri/lbg/nsc (private, limited by guarantee, no share capital, use of 'limited' exemption)",
            'публічна компанія великобританії з обмеженою відповідальністю':
                'united kingdom societas',
            'консорціум великобританії': 'united kingdom economic interest grouping',
        }
        self.all_ukr_company_type_dict = self.put_all_objects_to_dict('name', "business_register",
                                                                      "CompanyType")
        self.all_eng_company_type_dict = self.put_all_objects_to_dict('name_eng',
                                                                      "business_register",
                                                                      "CompanyType")
        super().__init__()

    def translate_company_type_name_eng(self, name_eng):
        for key, value in self.COMPANY_TYPES_UK_EN.items():
            if value == name_eng:
                return key
        return None

    def create_company_type(self, name, name_eng):
        company_type = CompanyType.objects.create(name=name, name_eng=name_eng)
        self.all_ukr_company_type_dict[name] = company_type
        self.all_eng_company_type_dict[name_eng] = company_type
        print(f'New company type: id={company_type.id}, name={company_type.name}, name_eng={company_type.name_eng}')
        send_new_company_type_message(company_type)
        return company_type

    def save_or_get_company_type(self, type_from_record, locale):
        if locale == 'uk':
            name = type_from_record.lower()
            company_type = self.all_ukr_company_type_dict.get(name)
            if not company_type:
                name_eng = self.COMPANY_TYPES_UK_EN.get(name)
                company_type = self.create_company_type(name, name_eng)
        elif locale == 'en':
            name_eng = type_from_record.lower()
            company_type = self.all_eng_company_type_dict.get(name_eng)
            if not company_type:
                name = self.translate_company_type_name_eng(name_eng)
                company_type = self.create_company_type(name, name_eng)
        else:
            raise ValueError(f'This parameter is not valid - {locale}. Should be "uk" or "en"')
        return company_type
