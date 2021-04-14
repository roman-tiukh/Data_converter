import logging
from datetime import datetime, date

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
from stats.tasks import endpoints_cache_warm_up

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
            relationship_type = company_dict.get('relationship_type_uk')
            if relationship_type:
                relationship_type = relationship_type.lower()
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
                    relationship_type=relationship_type,
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
                        relationship_type=relationship_type,
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
            fullname_transcriptions_eng = pep_dict['names'].lower()
            last_job_title = pep_dict.get('last_job_title')
            if last_job_title:
                last_job_title = last_job_title.lower()
            last_employer = pep_dict.get('last_workplace')
            if last_employer:
                last_employer = last_employer.lower()
            info = pep_dict.get('wiki_uk')
            sanctions = pep_dict.get('reputation_sanctions_uk')
            criminal_record = pep_dict.get('reputation_convictions_uk')
            assets_info = pep_dict.get('reputation_assets_uk')
            criminal_proceedings = pep_dict.get('reputation_crimes_uk')
            wanted = pep_dict.get('reputation_manhunt_uk')
            date_of_birth = pep_dict['date_of_birth']
            place_of_birth = pep_dict.get('city_of_birth_uk')
            if place_of_birth and len(place_of_birth):
                place_of_birth = place_of_birth.lower()
            is_pep = pep_dict['is_pep']
            pep_type = pep_dict.get('type_of_official')
            if pep_type:
                pep_type = pep_type.lower()
            url = pep_dict['url']
            is_dead = pep_dict['died']
            termination_date = pep_dict.get('termination_date_human')
            # omitting empty string as a meaningless value
            if termination_date and not len(termination_date):
                termination_date = None
            reason_of_termination = pep_dict.get('reason_of_termination')
            if reason_of_termination:
                reason_of_termination = reason_of_termination.lower()
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
                    fullname_transcriptions_eng=fullname_transcriptions_eng,
                    last_job_title=last_job_title,
                    last_employer=last_employer,
                    info=info,
                    sanctions=sanctions,
                    criminal_record=criminal_record,
                    assets_info=assets_info,
                    criminal_proceedings=criminal_proceedings,
                    wanted=wanted,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    is_pep=is_pep,
                    pep_type=pep_type,
                    url=url,
                    is_dead=is_dead,
                    termination_date=termination_date,
                    reason_of_termination=reason_of_termination,
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
                if pep.last_employer != last_employer:
                    pep.last_employer = last_employer
                    update_fields.append('last_employer')
                if pep.info != info:
                    pep.info = info
                    update_fields.append('info')
                if pep.sanctions != sanctions:
                    pep.sanctions = sanctions
                    update_fields.append('sanctions')
                if pep.criminal_record != criminal_record:
                    pep.criminal_record = criminal_record
                    update_fields.append('criminal_record')
                if pep.assets_info != assets_info:
                    pep.assets_info = assets_info
                    update_fields.append('assets_info')
                if pep.criminal_proceedings != criminal_proceedings:
                    pep.criminal_proceedings = criminal_proceedings
                    update_fields.append('criminal_proceedings')
                if pep.wanted != wanted:
                    pep.wanted = wanted
                    update_fields.append('wanted')
                if pep.date_of_birth != date_of_birth:
                    pep.date_of_birth = date_of_birth
                    update_fields.append('date_of_birth')
                if pep.place_of_birth != place_of_birth:
                    pep.place_of_birth = place_of_birth
                    update_fields.append('place_of_birth')
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

            if len(related_companies_list):
                self.save_or_update_pep_related_companies(related_companies_list, pep)


class PepConverterFromDB(Converter):

    def __init__(self):
        self.host = settings.PEP_SOURCE_HOST
        self.port = settings.PEP_SOURCE_PORT
        self.database = settings.PEP_SOURCE_DATABASE
        self.user = settings.PEP_SOURCE_USER
        self.password = settings.PEP_SOURCE_PASSWORD
        self.peps_dict = self.put_objects_to_dict('code', 'business_register', 'Pep')
        self.outdated_peps_dict = self.put_objects_to_dict('code', 'business_register', 'Pep')
        self.peps_links_dict = self.put_objects_to_dict(
            'source_id',
            'business_register',
            'RelatedPersonsLink')
        self.outdated_peps_links_dict = self.put_objects_to_dict(
            'source_id',
            'business_register',
            'RelatedPersonsLink')
        self.peps_companies_dict = self.put_objects_to_dict(
            'source_id',
            'business_register',
            'CompanyLinkWithPep')
        self.outdated_peps_companies_dict = self.put_objects_to_dict(
            'source_id',
            'business_register',
            'CompanyLinkWithPep')
        self.peps_total_records_from_source = 0
        self.peps_links_total_records_from_source = 0
        self.peps_companies_total_records_from_source = 0

        self.invalid_data_counter = 0
        self.PEP_QUERY = ("""
            SELECT id, last_name, first_name, patronymic, 
            last_name_en, first_name_en, patronymic_en, names, is_pep, 
            dob, city_of_birth_uk, city_of_birth_en, 
            reputation_sanctions_uk, reputation_sanctions_en, 
            reputation_convictions_uk, reputation_convictions_en, 
            reputation_assets_uk, reputation_assets_en, 
            reputation_crimes_uk, reputation_crimes_en, 
            reputation_manhunt_uk, reputation_manhunt_en, wiki_uk, wiki_en, 
            type_of_official, reason_of_termination, termination_date 
            FROM core_person;
        """)
        self.PEPS_LINKS_QUERY = ("""
            SELECT from_person_id, to_person_id, 
            from_relationship_type, to_relationship_type, 
            date_established, date_confirmed, date_finished,
            id 
            FROM core_person2person;
        """)
        self.PEPS_COMPANIES_QUERY = ("""
            SELECT 
                p2c.from_person_id,
                p2c.to_company_id,
                p2c.date_established,
                p2c.date_confirmed,
                p2c.date_finished,
                p2c.category,
                company.edrpou,
                company.state_company,
                company.short_name_en,
                company.name,
                country.name_en,
                p2c.id
            FROM core_person2company p2c
            INNER JOIN core_company company on p2c.to_company_id=company.id
            LEFT JOIN (
                SELECT from_company_id, MAX(to_country_id) to_country_id
                FROM core_company2country
                where relationship_type = 'registered_in'
                GROUP BY from_company_id
            ) c2c on p2c.to_company_id = c2c.from_company_id
            LEFT JOIN core_country country on c2c.to_country_id = country.id;
        """)
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
            is_changed = False
            from_person_source_id = link[0]
            from_person = self.peps_dict.get(str(from_person_source_id))
            if not from_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {from_person_source_id}')
                self.invalid_data_counter += 1
                continue
            to_person_source_id = link[1]
            to_person = self.peps_dict.get(str(to_person_source_id))
            if not to_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {to_person_source_id}')
                self.invalid_data_counter += 1
                continue
            from_person_relationship_type = link[2]
            to_person_relationship_type = link[3]
            category = self.PEP_RELATIONSHIPS_TYPES_TO_CATEGORIES.get(from_person_relationship_type)
            start_date = link[4]
            confirmation_date = link[5]
            end_date = link[6]
            source_id = link[7]

            stored_link = self.peps_links_dict.get(source_id)
            if not stored_link:
                self.peps_links_dict[source_id] = RelatedPersonsLink.objects.create(
                    from_person_id=from_person.id,
                    to_person_id=to_person.id,
                    from_person_relationship_type=from_person_relationship_type,
                    to_person_relationship_type=to_person_relationship_type,
                    category=category,
                    start_date=start_date,
                    confirmation_date=confirmation_date,
                    end_date=end_date,
                    source_id=source_id
                )

                is_changed = True
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
                if stored_link.source_id != source_id:
                    stored_link.source_id = source_id
                    update_fields.append('source_id')
                if update_fields:
                    update_fields.append('updated_at')
                    stored_link.save(update_fields=update_fields)
                    is_changed = True
                if self.outdated_peps_links_dict.get(source_id):
                    del self.outdated_peps_links_dict[source_id]
            if is_changed:
                from_person.save(update_fields=['updated_at', ])
                to_person.save(update_fields=['updated_at', ])
        if self.outdated_peps_links_dict:
            for link in self.outdated_peps_links_dict.values():
                link.soft_delete()
                link.from_person.save(update_fields=['updated_at', ])
                link.to_person.save(update_fields=['updated_at', ])

    def create_company_link_with_pep(self, company, pep, category, start_date, confirmation_date,
                                     end_date, is_state_company, source_id):
        self.peps_companies_dict[source_id] = CompanyLinkWithPep.objects.create(
            company=company,
            pep=pep,
            category=category,
            start_date=start_date,
            confirmation_date=confirmation_date,
            end_date=end_date,
            is_state_company=is_state_company,
            source_id=source_id
        )

    def save_or_update_peps_companies(self, peps_companies_data):
        address_converter = AddressConverter()
        for link in peps_companies_data:
            is_changed = False
            pep_source_id = link[0]
            pep = self.peps_dict.get(str(pep_source_id))
            if not pep:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {pep_source_id}')
                self.invalid_data_counter += 1
                continue
            company_antac_id = link[1]
            start_date = link[2]
            confirmation_date = link[3]
            end_date = link[4]
            category = link[5]
            edrpou = link[6]
            is_state_company = link[7]
            company_name = link[9]
            country_name = link[10]
            source_id = link[11]
            country = address_converter.save_or_get_country(country_name) if country_name else None
            company = Company.include_deleted_objects.filter(antac_id=company_antac_id).first()
            if not company and edrpou:
                company = Company.include_deleted_objects.filter(
                    edrpou=edrpou,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if company:
                    company.antac_id = company_antac_id
                    company.save(update_fields=['antac_id', 'updated_at'])
            if not company:
                company = Company.objects.create(name=company_name, edrpou=edrpou, country=country,
                                                 code=company_name + edrpou, source=Company.ANTAC,
                                                 antac_id=company_antac_id, from_antac_only=True)
                self.create_company_link_with_pep(company, pep, category, start_date,
                                                  confirmation_date, end_date, is_state_company,
                                                  source_id)
                is_changed = True
            else:
                already_stored_link = self.peps_companies_dict.get(source_id)
                if not already_stored_link:
                    self.create_company_link_with_pep(company, pep, category, start_date,
                                                      confirmation_date, end_date, is_state_company,
                                                      source_id)
                    is_changed = True
                else:
                    update_fields = []
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
                    if already_stored_link.source_id != source_id:
                        already_stored_link.source_id = source_id
                        update_fields.append('source_id')
                    if update_fields:
                        update_fields.append('updated_at')
                        already_stored_link.save(update_fields=update_fields)
                        is_changed = True
                    if self.outdated_peps_companies_dict.get(source_id):
                        del self.outdated_peps_companies_dict[source_id]
            if is_changed:
                pep.save(update_fields=['updated_at', ])
        if self.outdated_peps_companies_dict:
            for link in self.outdated_peps_companies_dict.values():
                link.soft_delete()
                link.pep.save(update_fields=['updated_at', ])

    def parse_date_of_birth(self, date_of_birth):
        if isinstance(date_of_birth, date) or isinstance(date_of_birth, datetime):
            date_of_birth = date_of_birth.strftime('%Y-%m-%d')
        elif isinstance(date_of_birth, str):
            date_of_birth = date_of_birth.strip()
            if date_of_birth:
                try:
                    date_of_birth = datetime.strptime(
                        date_of_birth.strip(), '%d.%m.%Y',
                    ).strftime('%Y-%m-%d')
                except ValueError:
                    pass
            else:
                date_of_birth = None
        else:
            date_of_birth = None
        return date_of_birth

    def save_or_update_peps(self, peps_data):
        for pep_data in peps_data:
            source_id = pep_data[0]
            code = str(source_id)
            last_name = pep_data[1].lower()
            first_name = pep_data[2].lower()
            middle_name = pep_data[3].lower()
            fullname = f'{last_name} {first_name} {middle_name}'
            fullname_transcriptions_eng = pep_data[7].lower()
            is_pep = pep_data[8]
            date_of_birth = self.parse_date_of_birth(pep_data[9])
            place_of_birth = to_lower_string_if_exists(pep_data[10])
            sanctions = pep_data[12]
            criminal_record = pep_data[14]
            assets_info = pep_data[16]
            criminal_proceedings = pep_data[18]
            wanted = pep_data[20]
            info = pep_data[22]
            pep_type_number = pep_data[24]
            pep_type = self.PEP_TYPES.get(pep_type_number) if pep_type_number else None
            reason_of_termination_number = pep_data[25]
            reason_of_termination = (self.REASONS_OF_TERMINATION.get(reason_of_termination_number)
                                     if reason_of_termination_number else None)
            is_dead = (reason_of_termination_number == 1)
            termination_date = pep_data[26]
            pep = self.peps_dict.get(code)
            if not pep:
                pep = Pep.objects.create(
                    source_id=source_id,
                    code=code,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    fullname=fullname,
                    fullname_transcriptions_eng=fullname_transcriptions_eng,
                    is_pep=is_pep,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    sanctions=sanctions,
                    criminal_record=criminal_record,
                    assets_info=assets_info,
                    criminal_proceedings=criminal_proceedings,
                    wanted=wanted,
                    info=info,
                    pep_type=pep_type,
                    reason_of_termination=reason_of_termination,
                    is_dead=is_dead,
                    termination_date=termination_date,
                )
                self.peps_dict[code] = pep
            else:
                update_fields = []
                if pep.source_id != source_id:
                    pep.source_id = source_id
                    update_fields.append('source_id')
                if pep.first_name != first_name:
                    pep.first_name = first_name
                    update_fields.append('first_name')
                if pep.middle_name != middle_name:
                    pep.middle_name = middle_name
                    update_fields.append('middle_name')
                if pep.last_name != last_name:
                    pep.last_name = last_name
                    update_fields.append('last_name')
                if pep.fullname != fullname:
                    pep.fullname = fullname
                    update_fields.append('fullname')
                if pep.fullname_transcriptions_eng != fullname_transcriptions_eng:
                    pep.fullname_transcriptions_eng = fullname_transcriptions_eng
                    update_fields.append('fullname_transcriptions_eng')
                if pep.is_pep != is_pep:
                    pep.is_pep = is_pep
                    update_fields.append('is_pep')
                if pep.date_of_birth != date_of_birth:
                    pep.date_of_birth = date_of_birth
                    update_fields.append('date_of_birth')
                if pep.place_of_birth != place_of_birth:
                    pep.place_of_birth = place_of_birth
                    update_fields.append('place_of_birth')
                if pep.sanctions != sanctions:
                    pep.sanctions = sanctions
                    update_fields.append('sanctions')
                if pep.criminal_record != criminal_record:
                    pep.criminal_record = criminal_record
                    update_fields.append('criminal_record')
                if pep.assets_info != assets_info:
                    pep.assets_info = assets_info
                    update_fields.append('assets_info')
                if pep.criminal_proceedings != criminal_proceedings:
                    pep.criminal_proceedings = criminal_proceedings
                    update_fields.append('criminal_proceedings')
                if pep.wanted != wanted:
                    pep.wanted = wanted
                    update_fields.append('wanted')
                if pep.info != info:
                    pep.info = info
                    update_fields.append('info')
                if pep.pep_type != pep_type:
                    pep.pep_type = pep_type
                    update_fields.append('pep_type')
                if pep.reason_of_termination != reason_of_termination:
                    pep.reason_of_termination = reason_of_termination
                    update_fields.append('reason_of_termination')
                if pep.is_dead != is_dead:
                    pep.is_dead = is_dead
                    update_fields.append('is_dead')
                if pep.termination_date != termination_date:
                    pep.termination_date = termination_date
                    update_fields.append('termination_date')
                if len(update_fields):
                    update_fields.append('updated_at')
                    pep.save(update_fields=update_fields)
                del self.outdated_peps_dict[code]
        if self.outdated_peps_dict:
            for pep in self.outdated_peps_dict.values():
                pep.soft_delete()

    def process(self):
        peps_data, peps_links_data, pep_companies_data = self.get_data_from_source_db()
        self.peps_total_records_from_source = len(peps_data)
        self.peps_links_total_records_from_source = len(peps_links_data)
        self.peps_companies_total_records_from_source = len(pep_companies_data)
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

        self.report_init()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: process() started ...')
        converter = PepConverterFromDB()
        converter.process()
        self.report.update_finish = timezone.now()
        self.report.save()

        self.vacuum_analyze(table_list=['business_register_pep', ])
        endpoints_cache_warm_up(endpoints=['/api/pep/'])
        self.report.update_status = True
        peps_total_records = Pep.objects.all().count()
        if peps_total_records != converter.peps_total_records_from_source:
            self.report.update_status = False
            self.report.update_message = (f'Total records of PEP objects from source is '
                                          f'{converter.peps_total_records_from_source} '
                                          f'but in our DB it is {peps_total_records}. \n')
            self.report.save()
        peps_links_total_records = RelatedPersonsLink.objects.all().count()
        if peps_links_total_records != converter.peps_links_total_records_from_source:
            self.report.update_status = False
            self.report.update_message += (f'Total records of RelatedPersonsLink from source is '
                                           f'{converter.peps_links_total_records_from_source} '
                                           f'but in our DB it is {peps_links_total_records}. \n')
        peps_companies_total_records = CompanyLinkWithPep.objects.all().count()
        if peps_companies_total_records != converter.peps_companies_total_records_from_source:
            self.report.update_status = False
            self.report.update_message += (f'Total records of CompanyLinkWithPep from source is '
                                           f'{converter.peps_companies_total_records_from_source} '
                                           f'but in our DB it is {peps_companies_total_records}')
            self.report.save()

        self.update_register_field(settings.PEP_REGISTER_LIST, 'total_records', peps_total_records)
        self.report.save()

        self.report.invalid_data = converter.invalid_data_counter
        self.measure_changes('business_register', 'Pep')
        self.report.save()
        logger.info(f'{self.reg_name}: Report created successfully.')

        if self.report.update_status:
            logger.info(f'{self.reg_name}: Update finished unsuccessfully')
        else:
            logger.info(f'{self.reg_name}: Update finished unsuccessfully. See update_message')
