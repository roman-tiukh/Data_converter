import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from django.utils import timezone
from business_register.models.company_models import Company
from business_register.models.pep_models import Pep, PepRelatedPerson, CompanyLinkWithPep
from business_register.converter.business_converter import BusinessConverter
from data_ocean.downloader import Downloader
from data_ocean.models import RegistryUpdaterModel
from requests.auth import HTTPBasicAuth
from django.conf import settings


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

    def save_or_update_pep_related_persons(self, related_persons_list, pep):
        already_stored_pep_related_persons = list(PepRelatedPerson.objects.filter(pep=pep))
        for person_dict in related_persons_list:
            fullname = person_dict['person_uk'].lower()
            fullname_eng = person_dict.get('person_uk_en')
            if fullname_eng:
                fullname_eng = fullname_eng.lower()
            relationship_type = person_dict.get('relationship_type')
            if relationship_type:
                relationship_type = relationship_type.lower()
            relationship_type_eng = person_dict.get('relationship_type_en')
            if relationship_type_eng:
                relationship_type_eng = relationship_type_eng.lower()
            is_pep = person_dict['is_pep']
            start_date = person_dict.get('date_established')
            # omitting empty string as a meaningless value
            if start_date and not len(start_date):
                start_date = None
            confirmation_date = person_dict.get('date_confirmed')
            if confirmation_date and not len(confirmation_date):
                confirmation_date = None
            end_date = person_dict.get('date_finished')
            if end_date and not len(end_date):
                end_date = None

            already_stored = False
            if len(already_stored_pep_related_persons):
                for stored_person in already_stored_pep_related_persons:
                    if (stored_person.fullname == fullname
                            and stored_person.relationship_type == relationship_type):
                        already_stored = True
                        # ToDo: resolve the problem of having records of the same persons
                        #  with different data
                        # update_fields = []
                        # if stored_person.relationship_type_eng != relationship_type_eng:
                        #     stored_person.relationship_type_eng = relationship_type_eng
                        #     update_fields.append('relationship_type_eng')
                        # if stored_person.is_pep != is_pep:
                        #     stored_person.is_pep = is_pep
                        #     update_fields.append('is_pep')
                        # if stored_person.start_date != start_date:
                        #     stored_person.start_date = start_date
                        #     update_fields.append('start_date')
                        # if stored_person.confirmation_date != confirmation_date:
                        #     stored_person.confirmation_date = confirmation_date
                        #     update_fields.append('confirmation_date')
                        # if stored_person.end_date != end_date:
                        #     stored_person.end_date = end_date
                        #     update_fields.append('end_date')
                        # if len(update_fields):
                        #     stored_person.save(update_fields=update_fields)
                        break
            if not already_stored:
                PepRelatedPerson.objects.create(
                    pep=pep,
                    fullname=fullname,
                    fullname_eng=fullname_eng,
                    relationship_type=relationship_type,
                    relationship_type_eng=relationship_type_eng,
                    is_pep=is_pep,
                    start_date=start_date,
                    confirmation_date=confirmation_date,
                    end_date=end_date
                )

    def save_to_db(self, json_file, log_id=None):

        if log_id:
            print(f'save_to_db: log_id = {log_id}.')
            upd_obj = RegistryUpdaterModel.objects.filter(id=log_id).first()
            if not upd_obj:
                print(f"Can't find log record id={log_id} in db!")
                return
            upd_obj.update_start = timezone.now()
            upd_obj.save()

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
            related_persons_list = pep_dict.get('related_persons', [])
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

            if len(related_persons_list):
                self.save_or_update_pep_related_persons(related_persons_list, pep)
            if len(related_companies_list):
                self.save_or_update_pep_related_companies(related_companies_list, pep)

        if log_id:
            upd_obj.update_finish = timezone.now()
            upd_obj.update_status = True
            upd_obj.save()


class PepDownloader(Downloader):
    url = settings.BUSINESS_PEP_SOURCE_URL
    auth = HTTPBasicAuth(settings.BUSINESS_PEP_AUTH_USER, settings.BUSINESS_PEP_AUTH_PASSWORD)
    chunk_size = 16 * 1024 * 1024
    reg_name = 'business_pep'
