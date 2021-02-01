import logging

import psycopg2
import sshtunnel
from django.conf import settings
from django.utils import timezone
from requests.auth import HTTPBasicAuth

from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import Company
from business_register.models.pep_models import Pep, RelatedPersonsLink, CompanyLinkWithPep
from data_ocean.converter import Converter
from data_ocean.downloader import Downloader
from data_ocean.utils import to_lower_string_if_exists
from location_register.converter.address import AddressConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PepConverterFromJson(BusinessConverter):

    def __init__(self):
        super().__init__()

    def save_or_update_pep_related_companies(self, related_companies_list, pep):
        already_stored_pep_related_companies_links = list(CompanyLinkWithPep.objects.filter(pep=
                                                                                            pep))
        for company_dict in related_companies_list:
            company_name = company_dict.get('to_company_uk')
            if company_name:
                company_name = company_name.lower()
            company_name_eng = company_dict.get('to_company_en')
            if company_name_eng:
                company_name_eng = company_name_eng.lower()
            company_short_name_eng = company_dict.get('to_company_short_en')
            if company_short_name_eng:
                company_short_name_eng = company_short_name_eng.lower()
            relationship_type = company_dict.get('relationship_type_uk')
            if relationship_type:
                relationship_type = relationship_type.lower()
            relationship_type_eng = company_dict.get('relationship_type_en')
            if relationship_type_eng:
                relationship_type_eng = relationship_type_eng.lower()
            start_date = company_dict.get('date_established')
            # omitting empty string as a meaningless value
            if start_date and not len(start_date):
                start_date = None
            confirmation_date = company_dict.get('date_confirmed')
            if confirmation_date and not len(confirmation_date):
                confirmation_date = None
            end_date = company_dict.get('date_finished')
            if end_date and not len(end_date):
                end_date = None
            is_state_company = company_dict.get('to_company_is_state')
            edrpou = company_dict.get('to_company_edrpou')

            company = None
            if not edrpou:
                company = Company.objects.create(name=company_name, code=company_name + 'EMPTY',
                                                 from_antac_only=True)
            # ToDo: we need an additional check
            if edrpou:
                company = Company.objects.filter(edrpou=edrpou).first()
            if not company:
                company = Company.objects.create(name=company_name, edrpou=edrpou,
                                                 code=company_name + edrpou, from_antac_only=True)
                CompanyLinkWithPep.objects.create(
                    company=company,
                    pep=pep,
                    company_name_eng=company_name_eng,
                    company_short_name_eng=company_short_name_eng,
                    relationship_type=relationship_type,
                    relationship_type_eng=relationship_type_eng,
                    start_date=start_date,
                    confirmation_date=confirmation_date,
                    end_date=end_date,
                    is_state_company=is_state_company
                )
            else:
                already_stored = False
                if len(already_stored_pep_related_companies_links):
                    for stored_company_link in already_stored_pep_related_companies_links:
                        if stored_company_link.company == company:
                            already_stored = True
                            # ToDo: resolve the problem of having records of the same persons
                            #  with different data
                            break
                if not already_stored:
                    CompanyLinkWithPep.objects.create(
                        company=company,
                        pep=pep,
                        company_name_eng=company_name_eng,
                        company_short_name_eng=company_short_name_eng,
                        relationship_type=relationship_type,
                        relationship_type_eng=relationship_type_eng,
                        start_date=start_date,
                        confirmation_date=confirmation_date,
                        end_date=end_date,
                        is_state_company=is_state_company
                    )

    def save_to_db(self, json_file):
        data = self.load_json(json_file)
        for pep_dict in data:
            first_name = pep_dict['first_name'].lower()
            middle_name = pep_dict['patronymic'].lower()
            last_name = pep_dict['last_name'].lower()
            fullname = pep_dict['full_name'].lower()
            fullname_eng = pep_dict['full_name_en'].lower()
            fullname_transcriptions_eng = pep_dict['names'].lower()
            last_job_title = pep_dict.get('last_job_title')
            if last_job_title:
                last_job_title = last_job_title.lower()
            last_job_title_eng = pep_dict.get('last_job_title_en')
            if last_job_title_eng:
                last_job_title_eng = last_job_title_eng.lower()
            last_employer = pep_dict.get('last_workplace')
            if last_employer:
                last_employer = last_employer.lower()
            last_employer_eng = pep_dict.get('last_workplace_en')
            if last_employer_eng:
                last_employer_eng = last_employer_eng.lower()
            info = pep_dict.get('wiki_uk')
            info_eng = pep_dict.get('wiki_en')
            sanctions = pep_dict.get('reputation_sanctions_uk')
            sanctions_eng = pep_dict.get('reputation_sanctions_en')
            criminal_record = pep_dict.get('reputation_convictions_uk')
            criminal_record_eng = pep_dict.get('reputation_convictions_en')
            assets_info = pep_dict.get('reputation_assets_uk')
            assets_info_eng = pep_dict.get('reputation_assets_en')
            criminal_proceedings = pep_dict.get('reputation_crimes_uk')
            criminal_proceedings_eng = pep_dict.get('reputation_crimes_en')
            wanted = pep_dict.get('reputation_manhunt_uk')
            wanted_eng = pep_dict.get('reputation_manhunt_en')
            date_of_birth = pep_dict['date_of_birth']
            place_of_birth = pep_dict.get('city_of_birth_uk')
            if place_of_birth and len(place_of_birth):
                place_of_birth = place_of_birth.lower()
            place_of_birth_eng = pep_dict.get('city_of_birth_en')
            if place_of_birth_eng and len(place_of_birth_eng):
                place_of_birth_eng = place_of_birth_eng.lower()
            is_pep = pep_dict['is_pep']
            pep_type = pep_dict.get('type_of_official')
            if pep_type:
                pep_type = pep_type.lower()
            pep_type_eng = pep_dict.get('type_of_official_en')
            if pep_type_eng:
                pep_type_eng = pep_type_eng.lower()
            url = pep_dict['url']
            is_dead = pep_dict['died']
            termination_date = pep_dict.get('termination_date_human')
            # omitting empty string as a meaningless value
            if termination_date and not len(termination_date):
                termination_date = None
            reason_of_termination = pep_dict.get('reason_of_termination')
            if reason_of_termination:
                reason_of_termination = reason_of_termination.lower()
            reason_of_termination_eng = pep_dict.get('reason_of_termination_en')
            if reason_of_termination_eng:
                reason_of_termination_eng = reason_of_termination_eng.lower()
            related_companies_list = pep_dict.get('related_companies', [])
            source_id = pep_dict.get('id')
            code = str(source_id)
            pep = Pep.objects.filter(code=code).first()
            if not pep:
                pep = Pep.objects.create(
                    code=code,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    fullname=fullname,
                    fullname_eng=fullname_eng,
                    fullname_transcriptions_eng=fullname_transcriptions_eng,
                    last_job_title=last_job_title,
                    last_job_title_eng=last_job_title_eng,
                    last_employer=last_employer,
                    last_employer_eng=last_employer_eng,
                    info=info,
                    info_eng=info_eng,
                    sanctions=sanctions,
                    sanctions_eng=sanctions_eng,
                    criminal_record=criminal_record,
                    criminal_record_eng=criminal_record_eng,
                    assets_info=assets_info,
                    assets_info_eng=assets_info_eng,
                    criminal_proceedings=criminal_proceedings,
                    criminal_proceedings_eng=criminal_proceedings_eng,
                    wanted=wanted,
                    wanted_eng=wanted_eng,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    place_of_birth_eng=place_of_birth_eng,
                    is_pep=is_pep,
                    pep_type=pep_type,
                    pep_type_eng=pep_type_eng,
                    url=url,
                    is_dead=is_dead,
                    termination_date=termination_date,
                    reason_of_termination=reason_of_termination,
                    reason_of_termination_eng=reason_of_termination_eng,
                    source_id=source_id
                )
            else:
                update_fields = []
                if pep.first_name != first_name:
                    pep.first_name = first_name
                    update_fields.append('first_name')
                if pep.middle_name != middle_name:
                    pep.middle_name = middle_name
                    update_fields.append('middle_name')
                if pep.last_name != last_name:
                    pep.last_name = last_name
                    update_fields.append('last_name')
                if pep.fullname_transcriptions_eng != fullname_transcriptions_eng:
                    pep.fullname_transcriptions_eng = fullname_transcriptions_eng
                    update_fields.append('fullname_transcriptions_eng')
                if pep.last_job_title != last_job_title:
                    pep.last_job_title = last_job_title
                    update_fields.append('last_job_title')
                if pep.last_job_title_eng != last_job_title_eng:
                    pep.last_job_title_eng = last_job_title_eng
                    update_fields.append('last_job_title_eng')
                if pep.last_employer != last_employer:
                    pep.last_employer = last_employer
                    update_fields.append('last_employer')
                if pep.last_employer_eng != last_employer_eng:
                    pep.last_employer_eng = last_employer_eng
                    update_fields.append('last_employer_eng')
                if pep.info != info:
                    pep.info = info
                    update_fields.append('info')
                if pep.info_eng != info_eng:
                    pep.info_eng = info_eng
                    update_fields.append('info_eng')
                if pep.sanctions != sanctions:
                    pep.sanctions = sanctions
                    update_fields.append('sanctions')
                if pep.sanctions_eng != sanctions_eng:
                    pep.sanctions_eng = sanctions_eng
                    update_fields.append('sanctions_eng')
                if pep.criminal_record != criminal_record:
                    pep.criminal_record = criminal_record
                    update_fields.append('criminal_record')
                if pep.criminal_record_eng != criminal_record_eng:
                    pep.criminal_record_eng = criminal_record_eng
                    update_fields.append('criminal_record_eng')
                if pep.assets_info != assets_info:
                    pep.assets_info = assets_info
                    update_fields.append('assets_info')
                if pep.assets_info_eng != assets_info_eng:
                    pep.assets_info_eng = assets_info_eng
                    update_fields.append('assets_info_eng')
                if pep.criminal_proceedings != criminal_proceedings:
                    pep.criminal_proceedings = criminal_proceedings
                    update_fields.append('criminal_proceedings')
                if pep.criminal_proceedings_eng != criminal_proceedings_eng:
                    pep.criminal_proceedings_eng = criminal_proceedings_eng
                    update_fields.append('criminal_proceedings_eng')
                if pep.wanted != wanted:
                    pep.wanted = wanted
                    update_fields.append('wanted')
                if pep.wanted_eng != wanted_eng:
                    pep.wanted_eng = wanted_eng
                    update_fields.append('wanted_eng')
                if pep.date_of_birth != date_of_birth:
                    pep.date_of_birth = date_of_birth
                    update_fields.append('date_of_birth')
                if pep.place_of_birth != place_of_birth:
                    pep.place_of_birth = place_of_birth
                    update_fields.append('place_of_birth')
                if pep.place_of_birth_eng != place_of_birth_eng:
                    pep.place_of_birth_eng = place_of_birth_eng
                    update_fields.append('place_of_birth_eng')
                if pep.is_pep != is_pep:
                    pep.is_pep = is_pep
                    update_fields.append('is_pep')
                if pep.pep_type != pep_type:
                    pep.pep_type = pep_type
                    update_fields.append('pep_type')
                if pep.pep_type_eng != pep_type_eng:
                    pep.pep_type_eng = pep_type_eng
                    update_fields.append('pep_type_eng')
                if pep.is_dead != is_dead:
                    pep.is_dead = is_dead
                    update_fields.append('is_dead')
                if pep.termination_date != termination_date:
                    pep.termination_date = termination_date
                    update_fields.append('termination_date')
                if pep.reason_of_termination != reason_of_termination:
                    pep.reason_of_termination = reason_of_termination
                    update_fields.append('reason_of_termination')
                if pep.reason_of_termination_eng != reason_of_termination_eng:
                    pep.reason_of_termination_eng = reason_of_termination_eng
                    update_fields.append('reason_of_termination_eng')
                if pep.source_id != source_id:
                    pep.source_id = source_id
                    update_fields.append('source_id')
                if len(update_fields):
                    update_fields.append('updated_at')
                    pep.save(update_fields=update_fields)

            if len(related_companies_list):
                self.save_or_update_pep_related_companies(related_companies_list, pep)


class PepConverterFromDB(Converter):

    def __init__(self):
        self.host = settings.PEP_SOURCE_HOST
        self.port = settings.PEP_SOURCE_PORT
        self.database = settings.PEP_SOURCE_DATABASE
        self.user = settings.PEP_SOURCE_USER
        self.password = settings.PEP_SOURCE_PASSWORD
        self.all_peps_dict = self.put_all_objects_to_dict('code', 'business_register', 'Pep')
        self.PEP_QUERY = ('SELECT id, last_name, first_name, patronymic, '
                          'last_name_en, first_name_en, patronymic_en, names, is_pep, '
                          'dob, city_of_birth_uk, city_of_birth_en, '
                          'reputation_sanctions_uk, reputation_sanctions_en, '
                          'reputation_convictions_uk, reputation_convictions_en, '
                          'reputation_assets_uk, reputation_assets_en, '
                          'reputation_crimes_uk, reputation_crimes_en, '
                          'reputation_manhunt_uk, reputation_manhunt_en, wiki_uk, wiki_en, '
                          'type_of_official, reason_of_termination, termination_date '
                          'FROM core_person;'
                          )
        self.PEPS_LINKS_QUERY = ('SELECT from_person_id, to_person_id, '
                                 'from_relationship_type, to_relationship_type, '
                                 'date_established, date_confirmed, date_finished '
                                 'FROM core_person2person;')
        self.PEPS_COMPANIES_QUERY = ('SELECT from_person_id, to_company_id, '
                                     'core_person2company.date_established, core_person2company.date_confirmed, '
                                     'core_person2company.date_finished, '
                                     'category, edrpou, state_company, short_name_en, core_company.name, '
                                     'core_country.name_en '
                                     'FROM core_person2company '
                                     'INNER JOIN core_company on to_company_id=core_company.id '
                                     'INNER JOIN core_company2country on to_company_id = core_company2country.from_company_id '
                                     'INNER JOIN core_country on to_country_id = core_country.id;')
        self.REASONS_OF_TERMINATION = {
            1: Pep.DIED,
            2: Pep.RESIGNED,
            3: Pep.LINKED_PEP_DIED,
            4: Pep.LINKED_PEP_RESIGNED,
            5: Pep.LEGISLATION_CHANGED,
            6: Pep.COMPANY_STATUS_CHANGED,
        }
        self.PEP_TYPES = {
            1: Pep.NATIONAL_PEP,
            2: Pep.FOREIGN_PEP,
            3: Pep.PEP_FROM_INTERNATIONAL_ORGANISATION,
            4: Pep.PEP_ASSOCIATED_PERSON,
            5: Pep.PEP_FAMILY_MEMBER,
        }
        self.PEP_RELATIONSHIPS_TYPES_TO_CATEGORIES = {
            "ділові зв'язки": RelatedPersonsLink.BUSINESS,
            "особисті зв'язки": RelatedPersonsLink.PERSONAL,
            'особи, які спільно проживають': RelatedPersonsLink.FAMILY,
            "пов'язані спільним побутом і мають взаємні права та обов'язки": RelatedPersonsLink.FAMILY,
            'усиновлювач': RelatedPersonsLink.FAMILY,
            'падчерка': RelatedPersonsLink.FAMILY,
            'дід': RelatedPersonsLink.FAMILY,
            'рідний брат': RelatedPersonsLink.FAMILY,
            'мати': RelatedPersonsLink.FAMILY,
            'син': RelatedPersonsLink.FAMILY,
            'невістка': RelatedPersonsLink.FAMILY,
            'внук': RelatedPersonsLink.FAMILY,
            'мачуха': RelatedPersonsLink.FAMILY,
            'особа, яка перебуває під опікою або піклуванням': RelatedPersonsLink.FAMILY,
            'усиновлений': RelatedPersonsLink.FAMILY,
            'внучка': RelatedPersonsLink.FAMILY,
            'батько': RelatedPersonsLink.FAMILY,
            'рідна сестра': RelatedPersonsLink.FAMILY,
            'зять': RelatedPersonsLink.FAMILY,
            'чоловік': RelatedPersonsLink.FAMILY,
            'опікун чи піклувальник': RelatedPersonsLink.FAMILY,
            'дочка': RelatedPersonsLink.FAMILY,
            'свекор': RelatedPersonsLink.FAMILY,
            'тесть': RelatedPersonsLink.FAMILY,
            'теща': RelatedPersonsLink.FAMILY,
            'баба': RelatedPersonsLink.FAMILY,
            'пасинок': RelatedPersonsLink.FAMILY,
            'вітчим': RelatedPersonsLink.FAMILY,
            'дружина': RelatedPersonsLink.FAMILY,
            'свекруха': RelatedPersonsLink.FAMILY,
        }

    def get_pep_data(self, host=None, port=None):

        host = host or self.host
        port = port or self.port

        logger.info(f'business_pep: psycopg2 connect to {host}:{port}...')
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        logger.info(f'business_pep: psycopg2 connection is active: {not connection.closed}')

        with connection.cursor() as cursor:
            cursor.execute(self.PEP_QUERY)
            pep_data = cursor.fetchall()
            logger.info(f'business_pep: psycopg2 result data length: {len(pep_data)} elements.')

            cursor.execute(self.PEPS_LINKS_QUERY)
            pep_links_data = cursor.fetchall()
            logger.info(f'business_pep: psycopg2 result data length: {len(pep_links_data)} elements.')

            cursor.execute(self.PEPS_COMPANIES_QUERY)
            pep_companies_data = cursor.fetchall()
            logger.info(f'business_pep: psycopg2 result data length: {len(pep_companies_data)} elements.')

        connection.close()

        return pep_data, pep_links_data, pep_companies_data

    def get_data_from_source_db(self):

        logger.info(f'business_pep: use SSH tunnel: {settings.PEP_SOURCE_USE_SSH}')

        if not settings.PEP_SOURCE_USE_SSH:
            return self.get_pep_data()

        sshtunnel.TUNNEL_TIMEOUT = settings.PEP_TUNNEL_TIMEOUT
        sshtunnel.SSH_TIMEOUT = settings.PEP_SSH_TIMEOUT
        with sshtunnel.SSHTunnelForwarder(
                (settings.PEP_SSH_SERVER_IP, settings.PEP_SSH_SERVER_PORT),
                ssh_username=settings.PEP_SSH_USERNAME,
                ssh_pkey=settings.PEP_SSH_PKEY,
                remote_bind_address=(self.host, self.port),
                # local_bind_address=(settings.PEP_LOCAL_SOURCE_HOST, settings.PEP_LOCAL_SOURCE_PORT)
        ) as tunnel:
            logger.info(
                f'business_pep: tunnel is active: {tunnel.is_active} on '
                f'{tunnel.local_bind_host}:{tunnel.local_bind_port}'
            )
            return self.get_pep_data(
                host=tunnel.local_bind_host,
                port=tunnel.local_bind_port,
            )

    def save_or_update_peps_links(self, peps_links_data):
        for link in peps_links_data:
            from_person_source_id = link[0]
            from_person = self.all_peps_dict.get(str(from_person_source_id))
            if not from_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {from_person_source_id}')
                continue
            to_person_source_id = link[1]
            to_person = self.all_peps_dict.get(str(to_person_source_id))
            if not to_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {to_person_source_id}')
                continue
            from_person_relationship_type = link[2]
            to_person_relationship_type = link[3]
            category = self.PEP_RELATIONSHIPS_TYPES_TO_CATEGORIES.get(from_person_relationship_type)
            start_date = link[4]
            confirmation_date = link[5]
            end_date = link[6]

            stored_link = RelatedPersonsLink.objects.filter(
                from_person_id=from_person.id, to_person_id=to_person.id
            ).first()
            if not stored_link:
                RelatedPersonsLink.objects.create(
                    from_person_id=from_person.id,
                    to_person_id=to_person.id,
                    from_person_relationship_type=from_person_relationship_type,
                    to_person_relationship_type=to_person_relationship_type,
                    category=category,
                    start_date=start_date,
                    confirmation_date=confirmation_date,
                    end_date=end_date
                )
            else:
                update_fields = []
                if stored_link.from_person_relationship_type != from_person_relationship_type:
                    stored_link.from_person_relationship_type = from_person_relationship_type
                    update_fields.append('from_person_relationship_type')
                if stored_link.to_person_relationship_type != to_person_relationship_type:
                    stored_link.to_person_relationship_type = to_person_relationship_type
                    update_fields.append('to_person_relationship_type')
                if stored_link.category != category:
                    stored_link.category = category
                    update_fields.append('category')
                if stored_link.start_date != start_date:
                    stored_link.start_date = start_date
                    update_fields.append('start_date')
                if stored_link.confirmation_date != confirmation_date:
                    stored_link.confirmation_date = confirmation_date
                    update_fields.append('confirmation_date')
                if stored_link.end_date != end_date:
                    stored_link.end_date = end_date
                    update_fields.append('end_date')
                if update_fields:
                    update_fields.append('updated_at')
                    stored_link.save(update_fields=update_fields)

    def create_company_link_with_pep(self, company, pep, company_short_name_eng, category,
                                     start_date, confirmation_date, end_date, is_state_company):
        CompanyLinkWithPep.objects.create(
            company=company,
            pep=pep,
            company_short_name_eng=company_short_name_eng,
            category=category,
            start_date=start_date,
            confirmation_date=confirmation_date,
            end_date=end_date,
            is_state_company=is_state_company
        )

    def save_or_update_peps_companies(self, peps_companies_data):
        address_converter = AddressConverter()
        for link in peps_companies_data:
            pep_source_id = link[0]
            pep = self.all_peps_dict.get(str(pep_source_id))
            if not pep:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {pep_source_id}')
                continue
            company_antac_id = link[1]
            start_date = to_lower_string_if_exists(link[2])
            confirmation_date = to_lower_string_if_exists(link[3])
            end_date = to_lower_string_if_exists(link[4])
            category = link[5]
            edrpou = link[6]
            is_state_company = link[7]
            company_short_name_eng = link[8]
            company_name = link[9]
            country_name = link[10]
            country = address_converter.save_or_get_country(country_name) if country_name else None
            company = Company.objects.filter(antac_id=company_antac_id).first()
            if company and company.from_antac_only:
                company.country = country
                company.save(update_fields=['country', 'updated_at'])
            if not company and edrpou:
                # ToDo: use source instead country after storing source in the server DB
                company = Company.objects.filter(edrpou=edrpou, country__name='ukraine').first()
                if company:
                    company.antac_id = company_antac_id
                    company.save(update_fields=['antac_id', 'updated_at'])
            if not company:
                company = Company.objects.create(name=company_name, edrpou=edrpou, country=country,
                                                 code=company_name + edrpou, source=Company.ANTAC,
                                                 antac_id=company_antac_id, from_antac_only=True)
                self.create_company_link_with_pep(company, pep, company_short_name_eng, category,
                                                  start_date, confirmation_date, end_date,
                                                  is_state_company)
            else:
                already_stored_link = CompanyLinkWithPep.objects.filter(pep=pep, company=company).first()
                if already_stored_link:
                    update_fields = []
                    if already_stored_link.company_short_name_eng != company_short_name_eng:
                        already_stored_link.company_short_name_eng = company_short_name_eng
                        update_fields.append('company_short_name_eng')
                    if already_stored_link.category != category:
                        already_stored_link.category = category
                        update_fields.append('category')
                    if already_stored_link.start_date != start_date:
                        already_stored_link.start_date = start_date
                        update_fields.append('start_date')
                    if already_stored_link.confirmation_date != confirmation_date:
                        already_stored_link.confirmation_date = confirmation_date
                        update_fields.append('confirmation_date')
                    if already_stored_link.end_date != end_date:
                        already_stored_link.end_date = end_date
                        update_fields.append('end_date')
                    if already_stored_link.is_state_company != is_state_company:
                        already_stored_link.is_state_company = is_state_company
                        update_fields.append('is_state_company')
                    if update_fields:
                        update_fields.append('updated_at')
                        already_stored_link.save(update_fields=update_fields)
                else:
                    self.create_company_link_with_pep(company, pep, company_short_name_eng, category,
                                                      start_date, confirmation_date, end_date,
                                                      is_state_company)

    def save_or_update_peps(self, peps_data):
        for pep_data in peps_data:
            source_id = pep_data[0]
            code = str(source_id)
            last_name = pep_data[1].lower()
            first_name = pep_data[2].lower()
            middle_name = pep_data[3].lower()
            fullname = f'{last_name} {first_name} {middle_name}'
            fullname_eng = f'{pep_data[4]} {pep_data[5]} {pep_data[6]}'.lower()
            fullname_transcriptions_eng = pep_data[7].lower()
            is_pep = pep_data[8]
            date_of_birth = to_lower_string_if_exists(pep_data[9])
            place_of_birth = to_lower_string_if_exists(pep_data[10])
            place_of_birth_eng = to_lower_string_if_exists(pep_data[11])
            sanctions = pep_data[12]
            sanctions_eng = pep_data[13]
            criminal_record = pep_data[14]
            criminal_record_eng = pep_data[15]
            assets_info = pep_data[16]
            assets_info_eng = pep_data[17]
            criminal_proceedings = pep_data[18]
            criminal_proceedings_eng = pep_data[19]
            wanted = pep_data[20]
            wanted_eng = pep_data[21]
            info = pep_data[22]
            info_eng = pep_data[23]
            pep_type_number = pep_data[24]
            pep_type = self.PEP_TYPES.get(pep_type_number) if pep_type_number else None
            reason_of_termination_number = to_lower_string_if_exists(pep_data[25])
            reason_of_termination = (self.PEP_TYPES.get(reason_of_termination_number)
                                     if reason_of_termination_number else None)
            is_dead = (reason_of_termination_number == 1)
            termination_date = to_lower_string_if_exists(pep_data[26])
            pep = self.all_peps_dict.get(code)
            if not pep:
                pep = Pep.objects.create(
                    code=code,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    fullname=fullname,
                    fullname_eng=fullname_eng,
                    fullname_transcriptions_eng=fullname_transcriptions_eng,
                    info=info,
                    info_eng=info_eng,
                    sanctions=sanctions,
                    sanctions_eng=sanctions_eng,
                    criminal_record=criminal_record,
                    criminal_record_eng=criminal_record_eng,
                    assets_info=assets_info,
                    assets_info_eng=assets_info_eng,
                    criminal_proceedings=criminal_proceedings,
                    criminal_proceedings_eng=criminal_proceedings_eng,
                    wanted=wanted,
                    wanted_eng=wanted_eng,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    place_of_birth_eng=place_of_birth_eng,
                    is_pep=is_pep,
                    pep_type=pep_type,
                    is_dead=is_dead,
                    termination_date=termination_date,
                    reason_of_termination=reason_of_termination,
                    source_id=source_id
                )
                self.all_peps_dict[code] = pep
            else:
                update_fields = []
                if pep.first_name != first_name:
                    pep.first_name = first_name
                    update_fields.append('first_name')
                if pep.middle_name != middle_name:
                    pep.middle_name = middle_name
                    update_fields.append('middle_name')
                if pep.last_name != last_name:
                    pep.last_name = last_name
                    update_fields.append('last_name')
                if pep.fullname_transcriptions_eng != fullname_transcriptions_eng:
                    pep.fullname_transcriptions_eng = fullname_transcriptions_eng
                    update_fields.append('fullname_transcriptions_eng')
                if pep.info != info:
                    pep.info = info
                    update_fields.append('info')
                if pep.info_eng != info_eng:
                    pep.info_eng = info_eng
                    update_fields.append('info_eng')
                if pep.sanctions != sanctions:
                    pep.sanctions = sanctions
                    update_fields.append('sanctions')
                if pep.sanctions_eng != sanctions_eng:
                    pep.sanctions_eng = sanctions_eng
                    update_fields.append('sanctions_eng')
                if pep.criminal_record != criminal_record:
                    pep.criminal_record = criminal_record
                    update_fields.append('criminal_record')
                if pep.criminal_record_eng != criminal_record_eng:
                    pep.criminal_record_eng = criminal_record_eng
                    update_fields.append('criminal_record_eng')
                if pep.assets_info != assets_info:
                    pep.assets_info = assets_info
                    update_fields.append('assets_info')
                if pep.assets_info_eng != assets_info_eng:
                    pep.assets_info_eng = assets_info_eng
                    update_fields.append('assets_info_eng')
                if pep.criminal_proceedings != criminal_proceedings:
                    pep.criminal_proceedings = criminal_proceedings
                    update_fields.append('criminal_proceedings')
                if pep.criminal_proceedings_eng != criminal_proceedings_eng:
                    pep.criminal_proceedings_eng = criminal_proceedings_eng
                    update_fields.append('criminal_proceedings_eng')
                if pep.wanted != wanted:
                    pep.wanted = wanted
                    update_fields.append('wanted')
                if pep.wanted_eng != wanted_eng:
                    pep.wanted_eng = wanted_eng
                    update_fields.append('wanted_eng')
                if pep.date_of_birth != date_of_birth:
                    pep.date_of_birth = date_of_birth
                    update_fields.append('date_of_birth')
                if pep.place_of_birth != place_of_birth:
                    pep.place_of_birth = place_of_birth
                    update_fields.append('place_of_birth')
                if pep.place_of_birth_eng != place_of_birth_eng:
                    pep.place_of_birth_eng = place_of_birth_eng
                    update_fields.append('place_of_birth_eng')
                if pep.is_pep != is_pep:
                    pep.is_pep = is_pep
                    update_fields.append('is_pep')
                if pep.pep_type != pep_type:
                    pep.pep_type = pep_type
                    update_fields.append('pep_type')
                if pep.is_dead != is_dead:
                    pep.is_dead = is_dead
                    update_fields.append('is_dead')
                if pep.termination_date != termination_date:
                    pep.termination_date = termination_date
                    update_fields.append('termination_date')
                if pep.reason_of_termination != reason_of_termination:
                    pep.reason_of_termination = reason_of_termination
                    update_fields.append('reason_of_termination')
                if pep.source_id != source_id:
                    pep.source_id = source_id
                    update_fields.append('source_id')
                if len(update_fields):
                    update_fields.append('updated_at')
                    pep.save(update_fields=update_fields)

    def process(self):
        peps_data, peps_links_data, pep_companies_data = self.get_data_from_source_db()
        logger.info(f'business_pep: save_or_update_peps started with {len(peps_data)} elements ...')
        self.save_or_update_peps(peps_data)
        logger.info(f'business_pep: save_or_update_peps finished.')

        logger.info(f'business_pep: save_pep_links started with {len(peps_links_data)} elements ...')
        self.save_or_update_peps_links(peps_links_data)
        logger.info(f'business_pep: save_pep_links finish.')

        logger.info(f'business_pep: save_pep_links started with {len(pep_companies_data)} elements ...')
        self.save_or_update_peps_companies(pep_companies_data)
        logger.info(f'business_pep: save_pep_links finish.')


class PepDownloader(Downloader):
    url = settings.BUSINESS_PEP_SOURCE_URL
    auth = HTTPBasicAuth(settings.BUSINESS_PEP_AUTH_USER, settings.BUSINESS_PEP_AUTH_PASSWORD)
    chunk_size = 16 * 1024 * 1024
    reg_name = 'business_pep'

    def get_source_file_name(self):
        now = timezone.now()
        return f'{self.reg_name}_{now.date()}_{now.hour:02}-{now.minute:02}'

    def update(self):
        logger.info(f'{self.reg_name}: Update started...')

        self.log_init()

        self.log_obj.update_start = timezone.now()
        self.log_obj.save()

        logger.info(f'{self.reg_name}: process() started ...')
        PepConverterFromDB().process()
        logger.info(f'{self.reg_name}: process() finished successfully.')

        self.log_obj.update_finish = timezone.now()
        self.log_obj.update_status = True
        self.log_obj.save()

        self.vacuum_analyze(table_list=['business_register_pep', ])

        new_total_records = Pep.objects.count()
        self.update_field(settings.ALL_PEPS_DATASET_NAME, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update finished successfully.')
