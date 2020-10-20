import logging
from django.utils import timezone
import psycopg2
import sshtunnel
from business_register.models.company_models import Company
from business_register.models.pep_models import Pep, RelatedPersonsLink, CompanyLinkWithPep
from business_register.converter.business_converter import BusinessConverter
from data_ocean.downloader import Downloader
from requests.auth import HTTPBasicAuth
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PepConverter(BusinessConverter):

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
            code = str(pep_dict.get('id'))
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
                if pep.url != url:
                    pep.url = url
                    update_fields.append('url')
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
                if len(update_fields):
                    pep.save(update_fields=update_fields)

            if len(related_companies_list):
                self.save_or_update_pep_related_companies(related_companies_list, pep)


class PepLinksLoader:

    def __init__(self):
        self.host = settings.PEP_SOURCE_HOST
        self.database = settings.PEP_SOURCE_DATABASE
        self.user = settings.PEP_SOURCE_USER
        self.password = settings.PEP_SOURCE_PASSWORD
        self.QUERY = ('SELECT from_person_id, to_person_id, from_relationship_type, '
                      'to_relationship_type, date_established, date_confirmed, date_finished '
                      'FROM core_person2person;')

    def get_data_from_prod_source_db(self):
        sshtunnel.TUNNEL_TIMEOUT = settings.PEP_PROD_TUNNEL_TIMEOUT
        sshtunnel.SSH_TIMEOUT = settings.PEP_PROD_SSH_TIMEOUT
        with sshtunnel.SSHTunnelForwarder(
                (settings.PEP_PROD_SSH_SERVER_IP, settings.PEP_PROD_SSH_SERVER_PORT),
                ssh_username=settings.PEP_PROD_SSH_USERNAME,
                ssh_pkey=settings.PEP_PROD_SSH_PKEY,
                remote_bind_address=(settings.PEP_PROD_DB_SERVER_IP, settings.PEP_PROD_DB_SERVER_PORT),
                # local_bind_address=(settings.PEP_PROD_MAP_DB_SERVER_IP, settings.PEP_PROD_MAP_DB_SERVER_PORT)
        ) as tunnel:
            connection = psycopg2.connect(
                host=tunnel.local_bind_host,
                port=tunnel.local_bind_port,
                database=settings.PEP_PROD_DB_NAME,
                user=settings.PEP_PROD_DB_USER,
                password=settings.PEP_PROD_DB_PASSWORD
            )
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(self.QUERY)
                    data = cursor.fetchall()
            connection.close()
            return data

    def get_data_from_source_db(self):
        connection = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(self.QUERY)
                data = cursor.fetchall()
        if connection:
            connection.close()
        return data

    def save_pep_links(self, data):
        for link in data:
            from_person_source_db_id = str(link[0])
            from_person = Pep.objects.filter(code=from_person_source_db_id).first()
            if not from_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {from_person_source_db_id}')
                continue
            to_person_source_db_id = str(link[1])
            to_person = Pep.objects.filter(code=to_person_source_db_id).first()
            if not to_person:
                logger.info(f'No such pep in our DB. '
                            f'Check records in the source DB with id {to_person_source_db_id}')
                continue
            from_person_relationship_type = link[2]
            to_person_relationship_type = link[3]
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
                    stored_link.save(update_fields=update_fields)

    def process(self):
        data = self.get_data_from_source_db()
        self.save_pep_links(data)

    def process_prod(self):
        data = self.get_data_from_prod_source_db()
        logger.info(f'PEP len(data): {len(data)}')
        print(f'PEP len(data): {len(data)}')
        self.save_pep_links(data)


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
        self.download()

        self.log_obj.update_start = timezone.now()
        self.log_obj.save()

        logger.info(f'{self.reg_name}: CompanyLinkWithPep.truncate() started...')
        CompanyLinkWithPep.truncate()
        logger.info(f'{self.reg_name}: CompanyLinkWithPep.truncate() finished successfully.')

        logger.info(f'{self.reg_name}: Company.objects.filter(from_antac_only=True).delete() started...')
        Company.objects.filter(from_antac_only=True).delete()
        logger.info(f'{self.reg_name}: Company.objects.filter(from_antac_only=True).delete() finished successfully.')

        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) started ...')
        PepConverter().save_to_db(self.file_path)
        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) finished successfully.')

        self.log_obj.update_finish = timezone.now()
        self.log_obj.update_status = True
        self.log_obj.save()

        self.remove_file()

        self.vacuum_analyze(table_list=['business_register_pep', ])

        logger.info(f'{self.reg_name}: PepLinksLoader().process() started...')
        # PepLinksLoader().process()
        PepLinksLoader().process_prod()
        logger.info(f'{self.reg_name}: PepLinksLoader().process() finished successfully.')

        logger.info(f'{self.reg_name}: Update finished successfully.')
