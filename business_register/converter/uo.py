import re

from django.conf import settings

from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import (
    Assignee, BancruptcyReadjustment, Bylaw, Company, CompanyDetail, CompanyToKved,
    CompanyToPredecessor, CompanyType, ExchangeDataCompany, FounderFull, Predecessor,
    Signer, TerminationStarted
)
from data_ocean.converter import BulkCreateUpdateManager
from data_ocean.utils import cut_first_word, format_date_to_yymmdd, get_first_word


class Parser(BusinessConverter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = settings.CHUNK_SIZE_UO
    RECORD_TAG = 'SUBJECT'
    all_bylaw_dict = {}
    all_company_type_dict = {}
    all_predecessors_dict = {}
    company_update_dict = {}
    company_create_dict = {}
    branch_to_parent = {}
    tables = [
        BancruptcyReadjustment,
        # Bylaw,
        Company,
        CompanyDetail,
        CompanyToKved,
        CompanyToPredecessor,
        # CompanyType,
        ExchangeDataCompany,
        FounderFull,
        # Status,
        # Authority,
        # Predecessor,
        Signer,
        TerminationStarted
    ]
    bulk_manager = BulkCreateUpdateManager(100000)
    branch_bulk_manager = BulkCreateUpdateManager(100000)

    def __init__(self):
        self.all_bylaw_dict = self.put_all_objects_to_dict("name", "business_register", "Bylaw")
        self.all_company_type_dict = self.put_all_objects_to_dict(
            "name", "business_register", "CompanyType"
        )
        self.all_predecessors_dict = self.put_all_objects_to_dict(
            "name", "business_register", "Predecessor"
        )

        super().__init__()

    def save_or_get_bylaw(self, value):
        if not value in self.all_bylaw_dict:
            self.bylaw = Bylaw(name=value)
            self.bylaw.save()
            self.all_bylaw_dict[value] = self.bylaw
        else:
            self.bylaw = self.all_bylaw_dict[value]
        return self.bylaw

    def save_or_get_company_type(self, value):
        if not value in self.all_company_type_dict:
            self.company_type = CompanyType(name=value)
            self.company_type.save()
            self.all_company_type_dict[value] = self.company_type
        else:
            self.company_type = self.all_company_type_dict[value]

    def save_or_get_predecessor(self, item):
        if not item.xpath('NAME')[0].text in self.all_predecessors_dict:
            self.predecessor = Predecessor(
                name=item.xpath('NAME')[0].text,
                code=item.xpath('CODE')[0].text
            )
            self.predecessor.save()
            self.all_predecessors_dict[item.xpath('NAME')[0].text] = self.predecessor
            return self.predecessor
        else:
            self.predecessor = self.all_predecessors_dict[item.xpath('NAME')[0].text]
            return self.predecessor

    def create_hash_code(self, name, edrpou):
        return name + edrpou

    def company_create(self, record, edrpou, registration_date, registration_info):
        company = Company()
        company.name = record.xpath('NAME')[0].text
        company.short_name = record.xpath('SHORT_NAME')[0].text
        company.company_type = self.company_type
        company.edrpou = edrpou
        company.address = record.xpath('ADDRESS')[0].text
        company.status = self.status
        company.bylaw = self.bylaw
        company.registration_date = registration_date
        company.registration_info = registration_info
        company.contact_info = record.xpath('CONTACTS')[0].text
        company.authority = self.authority
        company.hash_code = self.create_hash_code(record.xpath('NAME')[0].text, edrpou)
        return company

    def branch_create(self, item, code):
        branch = Company()
        branch.name = item.xpath('NAME')[0].text
        branch.short_name = code
        branch.address = item.xpath('ADDRESS')[0].text
        if item.xpath('CREATE_DATE')[0].text:
            branch.registration_date = format_date_to_yymmdd(
                item.xpath('CREATE_DATE')[0].text
            ) or None
        branch.contact_info = item.xpath('CONTACTS')[0].text
        branch.authority = self.authority
        branch.bylaw = self.bylaw
        branch.company_type = self.company_type
        branch.status = self.status
        branch.hash_code = self.create_hash_code(branch.name, code)
        return branch

    def add_company_detail(self, record, edrpou):
        company_detail = CompanyDetail()
        company_detail.founding_document_number = record.xpath('FOUNDING_DOCUMENT_NUM')[0].text
        company_detail.executive_power = record.xpath('EXECUTIVE_POWER')[0].text
        company_detail.superior_management = record.xpath('SUPERIOR_MANAGEMENT')[0].text
        company_detail.authorized_capital = record.xpath('AUTHORIZED_CAPITAL')[0].text
        company_detail.managing_paper = record.xpath('MANAGING_PAPER')[0].text
        company_detail.terminated_info = record.xpath('TERMINATED_INFO')[0].text
        company_detail.termination_cancel_info = record.xpath('TERMINATION_CANCEL_INFO')[0].text
        company_detail.vp_dates = record.xpath('VP_DATES')[0].text
        company_detail.hash_code = self.create_hash_code(record.xpath('NAME')[0].text, edrpou)
        self.bulk_manager.add_create(company_detail)

    def add_assignees(self, record, hashcode):
        if len(record.xpath('ASSIGNEES')[0]) > 0:
            for item in record.xpath('ASSIGNEES')[0]:
                assignee = Assignee()
                assignee.name = item.xpath('NAME')[0].text
                assignee.edrpou = item.xpath('CODE')[0].text
                assignee.hash_code = hashcode
                self.bulk_manager.add_create(assignee)

    def add_bancruptcy_readjustment(self, record, edrpou):
        bancruptcy_readjustment = BancruptcyReadjustment()
        if record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE'):
            bancruptcy_readjustment.op_date = format_date_to_yymmdd(
                record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE')[0].text) or None
            bancruptcy_readjustment.reason = record.xpath(
                'BANKRUPTCY_READJUSTMENT_INFO/REASON')[0].text
            bancruptcy_readjustment.sbj_state = record.xpath(
                'BANKRUPTCY_READJUSTMENT_INFO/SBJ_STATE')[0].text
            bancruptcy_readjustment.head_name = record.xpath(
                'BANKRUPTCY_READJUSTMENT_INFO/BANKRUPTCY_READJUSTMENT_HEAD_NAME')[0].text
            bancruptcy_readjustment.hash_code = self.create_hash_code(
                record.xpath('NAME')[0].text, edrpou)
            self.bulk_manager.add_create(bancruptcy_readjustment)

    def add_company_to_kved(self, activity_kinds, name, edrpou):
        if len(activity_kinds) <= 0:
            return
        for item in activity_kinds:
            if not item.xpath('NAME'):
                continue
            kved_name = item.xpath('NAME')[0].text
            if not kved_name:
                continue
            company_to_kved = CompanyToKved()
            company_to_kved.kved = self.get_kved_from_DB(kved_name)
            company_to_kved.primary_kved = item.xpath('PRIMARY')[0].text == "так"
            company_to_kved.hash_code = self.create_hash_code(name, edrpou)
            self.bulk_manager.add_create(company_to_kved)

    def add_company_to_kved_branch(self, activity_kinds, name, code):
        if len(activity_kinds) > 0:
            for item in activity_kinds:
                company_to_kved = CompanyToKved()
                if item.xpath('CODE'):
                    company_to_kved.kved = self.get_kved_from_DB(item.xpath('CODE')[0].text)
                    company_to_kved.primary_kved = True if item.xpath(
                        'PRIMARY')[0].text == "так" else False
                    company_to_kved.hash_code = self.create_hash_code(name, code)
                    self.branch_bulk_manager.add_create(company_to_kved)

    def add_exchange_data(self, exchange_data, name, edrpou):
        if len(exchange_data) > 0:
            for item in exchange_data:
                exchange_answer = ExchangeDataCompany()
                if item.xpath('AUTHORITY_NAME'):
                    exchange_answer.authority = self.save_or_get_authority(item.xpath(
                        'AUTHORITY_NAME')[0].text)
                    tax_payer_type = item.xpath('TAX_PAYER_TYPE')[0].text or Company.INVALID
                    exchange_answer.taxpayer_type = self.save_or_get_taxpayer_type(tax_payer_type)
                    if item.xpath('START_DATE')[0].text:
                        exchange_answer.start_date = format_date_to_yymmdd(
                            item.xpath('START_DATE')[0].text) or None
                    exchange_answer.start_number = item.xpath('START_NUM')[0].text
                    if item.xpath('END_DATE')[0].text:
                        exchange_answer.end_date = format_date_to_yymmdd(
                            item.xpath('END_DATE')[0].text) or None
                    exchange_answer.end_number = item.xpath('END_NUM')[0].text
                    exchange_answer.hash_code = self.create_hash_code(name, edrpou)
                    self.bulk_manager.add_create(exchange_answer)

    def add_exchange_data_branch(self, exchange_data, name, code):
        if len(exchange_data) > 0:
            for item in exchange_data:
                exchange_answer = ExchangeDataCompany()
                if item.xpath('AUTHORITY_NAME'):
                    exchange_answer.authority = self.save_or_get_authority(
                        item.xpath('AUTHORITY_NAME')[0].text)
                    tax_payer_type = item.xpath('TAX_PAYER_TYPE')[0].text or Company.INVALID
                    exchange_answer.taxpayer_type = self.save_or_get_taxpayer_type(tax_payer_type)
                    if item.xpath('START_DATE')[0].text:
                        exchange_answer.start_date = format_date_to_yymmdd(
                            item.xpath('START_DATE')[0].text) or None
                    exchange_answer.start_number = item.xpath('START_NUM')[0].text
                    if item.xpath('END_DATE')[0].text:
                        exchange_answer.end_date = format_date_to_yymmdd(
                            item.xpath('END_DATE')[0].text) or None
                    exchange_answer.end_number = item.xpath('END_NUM')[0].text
                    exchange_answer.hash_code = self.create_hash_code(name, code)
                    self.branch_bulk_manager.add_create(exchange_answer)

    def extract_founder_data(self, string):
        splitted = string.split(',')
        name = splitted[0]
        second = splitted[1].strip()
        edrpou = second if len(second) == 8 and second.isdigit() else None
        equity = None
        piece = None
        for s in splitted:
            if s.startswith(' розмір внеску до статутного фонду') and s.endswith('грн.'):
                piece = s
                equity = float(re.findall("\d+\.\d+", s)[0])
                break
        address = string.replace(name, '')
        if edrpou:
            address = address.replace(edrpou, '')
        if piece:
            address = address.replace(piece, '')
        if len(address) < 15:
            address = None
        if len(address) > 200:
            address = None
        return name, edrpou, address, equity

    def add_founders(self, record, edrpou):
        if len(record.xpath('FOUNDERS')[0]) > 0:
            for item in record.xpath('FOUNDERS')[0]:
                founder = FounderFull()
                # checking if there is additional data except name
                if ',' in item.text:
                    founder.name, founder.edrpou, founder.address, founder.equity = \
                        self.extract_founder_data(item.text)
                else:
                    founder.name = item.text
                founder.hash_code = self.create_hash_code(record.xpath('NAME')[0].text, edrpou)
                self.bulk_manager.add_create(founder)

    def add_company_to_predecessors(self, record, edrpou):
        if len(record.xpath('PREDECESSORS')[0]) > 0:
            for item in record.xpath('PREDECESSORS')[0]:
                company_to_predecessor = CompanyToPredecessor()
                if item.xpath('NAME'):
                    company_to_predecessor.predecessor = self.save_or_get_predecessor(item)
                    company_to_predecessor.hash_code = self.create_hash_code(
                        record.xpath('NAME')[0].text, edrpou)
                    self.bulk_manager.add_create(company_to_predecessor)

    def add_signers(self, record, edrpou):
        if len(record.xpath('SIGNERS')[0]) > 0:
            for item in record.xpath('SIGNERS')[0]:
                signer = Signer()
                signer.name = item.text
                signer.hash_code = self.create_hash_code(record.xpath('NAME')[0].text, edrpou)
                self.bulk_manager.add_create(signer)

    def add_termination_started(self, record, edrpou):
        termination_started = TerminationStarted()
        if record.xpath('TERMINATION_STARTED_INFO/OP_DATE'):
            if record.xpath('TERMINATION_STARTED_INFO/OP_DATE')[0].text:
                termination_started.op_date = format_date_to_yymmdd(
                    record.xpath('TERMINATION_STARTED_INFO/OP_DATE')[0].text) or None
            termination_started.reason = record.xpath('TERMINATION_STARTED_INFO/REASON')[0].text
            termination_started.sbj_state = record.xpath(
                'TERMINATION_STARTED_INFO/SBJ_STATE')[0].text
            termination_started.signer_name = record.xpath(
                'TERMINATION_STARTED_INFO/SIGNER_NAME')[0].text
            if record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE')[0].text:
                termination_started.creditor_reg_end_date = format_date_to_yymmdd(
                    record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE')[0].text) or '01.01.1990'
            termination_started.hash_code = self.create_hash_code(
                record.xpath('NAME')[0].text, edrpou)
            self.bulk_manager.add_create(termination_started)

    def add_branches(self, record, edrpou):
        if len(record.xpath('BRANCHES')[0]) > 0:
            for item in record.xpath('BRANCHES')[0]:
                code = item.xpath('CODE')[0].text or Company.INVALID
                self.save_or_get_authority('EMP')
                self.save_or_get_bylaw('EMP')
                self.save_or_get_company_type('EMP')
                self.save_or_get_status('EMP')
                # try:
                #     branch = Company.objects.filter(
                #         hash_code=self.create_hash_code(item.xpath('NAME')[0].text, code)).first()
                # except:
                #     pass
                # if branch:
                #     branch.address = item.xpath('ADDRESS')[0].text
                #     if item.xpath('CREATE_DATE')[0].text:
                #         branch.registration_date = format_date_to_yymmdd(
                #             item.xpath('CREATE_DATE')[0].text) or None
                #     branch.contact_info = item.xpath('CONTACTS')[0].text
                #     self.branch_bulk_manager.add_update(branch)
                #     print('update')
                # else:
                #     branch = self.branch_create(item, code)
                #     self.branch_bulk_manager.add_create(branch)
                #     print('create')
                branch = self.branch_create(item, code)
                self.branch_bulk_manager.add_create(branch)

                self.add_company_to_kved_branch(
                    item.xpath('ACTIVITY_KINDS')[0],
                    item.xpath('NAME')[0].text, code
                )
                self.add_exchange_data_branch(
                    item.xpath('EXCHANGE_DATA')[0],
                    item.xpath('NAME')[0].text, code
                )
                if item.xpath('SIGNER'):
                    signer = Signer(
                        name=item.xpath('SIGNER')[0].text,
                        hash_code=self.create_hash_code(item.xpath('NAME')[0].text, code)
                    )
                    self.branch_bulk_manager.add_create(signer)
                self.branch_to_parent[
                    self.create_hash_code(item.xpath('NAME')[0].text, code)
                ] = self.create_hash_code(record.xpath('NAME')[0].text, edrpou)

    def save_to_db(self, records):
        self.bylaw = None
        self.company_type = None
        for record in records:
            self.authority = self.save_or_get_authority(record.xpath('CURRENT_AUTHORITY')[0].text)
            self.status = self.save_or_get_status(record.xpath('STAN')[0].text)
            self.save_or_get_bylaw(record.xpath('STATUTE')[0].text)
            self.save_or_get_company_type(record.xpath('OPF')[0].text)

            edrpou = record.xpath('EDRPOU')[0].text or Company.INVALID
            registration_date = None
            registration_info = None
            registration = record.xpath('REGISTRATION')[0].text
            if registration:
                registration_date = format_date_to_yymmdd(
                    get_first_word(registration)) or None
                registration_info = cut_first_word(registration) or None
            # try:
            #     company = Company.objects.filter(
            #         hash_code=self.create_hash_code(record.xpath('NAME')[0].text, edrpou)).first()
            #     company.short_name = record.xpath('SHORT_NAME')[0].text
            #     company.company_type = self.company_type
            #     company.address = record.xpath('ADDRESS')[0].text
            #     company.status = self.status
            #     company.bylaw = self.bylaw
            #     company.registration_date = registration_date
            #     company.registration_info = registration_info
            #     company.contact_info = record.xpath('CONTACTS')[0].text
            #     company.authority = self.authority
            #     self.bulk_manager.add_update(company)
            #
            #     print('update')
            # except:
            #
            #     company = self.company_create(record, edrpou, registration_date, registration_info)
            #     self.bulk_manager.add_create(company)
            #
            #     print('create')
            company = self.company_create(record, edrpou, registration_date, registration_info)
            self.bulk_manager.add_create(company)

            self.add_branches(record, edrpou)
            self.add_assignees(record, company.hash_code)
            self.add_company_detail(record, edrpou)
            self.add_company_to_kved(record.xpath(
                'ACTIVITY_KINDS')[0], record.xpath('NAME')[0].text, edrpou)
            self.add_bancruptcy_readjustment(record, edrpou)
            self.add_exchange_data(record.xpath('EXCHANGE_DATA')[0], record.xpath('NAME')[0].text, edrpou)
            self.add_founders(record, edrpou)
            self.add_company_to_predecessors(record, edrpou)
            self.add_signers(record, edrpou)
            self.add_termination_started(record, edrpou)

        if len(self.bulk_manager._update_queues['business_register.Company']) > 0:
            self.bulk_manager._commit_update(Company, ['name', 'short_name', 'company_type', 'edrpou'])
        self.bulk_manager._commit_create(Company)
        company_update_dict = {}
        company_create_dict = {}

        for company in self.bulk_manager._update_queues['business_register.Company']:
            company_update_dict[company.hash_code] = company
        for company in self.bulk_manager._create_queues['business_register.Company']:
            company_create_dict[company.hash_code] = company

        self.bulk_manager._update_queues['business_register.Company'] = []
        self.bulk_manager._create_queues['business_register.Company'] = []

        for branch in self.branch_bulk_manager._create_queues['business_register.Company']:
            if self.branch_to_parent[branch.hash_code] in company_update_dict:
                branch.parent = company_update_dict[self.branch_to_parent[branch.hash_code]]
            else:
                branch.parent = company_create_dict[self.branch_to_parent[branch.hash_code]]

        for branch in self.branch_bulk_manager._update_queues['business_register.Company']:
            if self.branch_to_parent[branch.hash_code] in company_update_dict:
                branch.parent = company_update_dict[self.branch_to_parent[branch.hash_code]]
            else:
                branch.parent = company_create_dict[self.branch_to_parent[branch.hash_code]]

        branch_to_parent = {}

        for assignee in self.bulk_manager._create_queues['business_register.Assignee']:
            if assignee.hash_code in company_update_dict:
                assignee.company = company_update_dict[assignee.hash_code]
            else:
                assignee.company = company_create_dict[assignee.hash_code]

        for company_to_kved in self.bulk_manager._create_queues['business_register.CompanyToKved']:
            if company_to_kved.hash_code in company_update_dict:
                company_to_kved.company = company_update_dict[company_to_kved.hash_code]
            else:
                company_to_kved.company = company_create_dict[company_to_kved.hash_code]

        for exchange_data in self.bulk_manager._create_queues['business_register.ExchangeDataCompany']:
            if exchange_data.hash_code in company_update_dict:
                exchange_data.company = company_update_dict[exchange_data.hash_code]
            else:
                exchange_data.company = company_create_dict[exchange_data.hash_code]

        for founder in self.bulk_manager._create_queues['business_register.FounderFull']:
            if founder.hash_code in company_update_dict:
                founder.company = company_update_dict[founder.hash_code]
            else:
                founder.company = company_create_dict[founder.hash_code]

        for bancruptcy_readjustment in self.bulk_manager._create_queues['business_register.BancruptcyReadjustment']:
            if bancruptcy_readjustment.hash_code in company_update_dict:
                bancruptcy_readjustment.company = company_update_dict[bancruptcy_readjustment.hash_code]
            else:
                bancruptcy_readjustment.company = company_create_dict[bancruptcy_readjustment.hash_code]

        for company_detail in self.bulk_manager._create_queues['business_register.CompanyDetail']:
            if company_detail.hash_code in company_update_dict:
                company_detail.company = company_update_dict[company_detail.hash_code]
            else:
                company_detail.company = company_create_dict[company_detail.hash_code]

        for company_to_predecessor in self.bulk_manager._create_queues['business_register.CompanyToPredecessor']:
            if company_to_predecessor.hash_code in company_update_dict:
                company_to_predecessor.company = company_update_dict[company_to_predecessor.hash_code]
            else:
                company_to_predecessor.company = company_create_dict[company_to_predecessor.hash_code]

        for signer in self.bulk_manager._create_queues['business_register.Signer']:
            if signer.hash_code in company_update_dict:
                signer.company = company_update_dict[signer.hash_code]
            else:
                signer.company = company_create_dict[signer.hash_code]

        for termination_started in self.bulk_manager._create_queues['business_register.TerminationStarted']:
            if termination_started.hash_code in company_update_dict:
                termination_started.company = company_update_dict[termination_started.hash_code]
            else:
                termination_started.company = company_create_dict[termination_started.hash_code]

        self.bulk_manager._commit_create(Assignee)
        self.bulk_manager._commit_create(FounderFull)
        self.bulk_manager._commit_create(BancruptcyReadjustment)
        self.bulk_manager._commit_create(CompanyDetail)
        self.bulk_manager._commit_create(CompanyToKved)
        self.bulk_manager._commit_create(ExchangeDataCompany)
        self.bulk_manager._commit_create(CompanyToPredecessor)
        self.bulk_manager._commit_create(Signer)
        self.bulk_manager._commit_create(TerminationStarted)
        if len(self.branch_bulk_manager._update_queues['business_register.Company']) > 0:
            self.branch_bulk_manager._commit_update(Company, ['name', 'short_name'])
        self.branch_bulk_manager._commit_create(Company)

        company_update_dict = {}
        company_create_dict = {}

        for company in self.branch_bulk_manager._update_queues['business_register.Company']:
            company_update_dict[company.hash_code] = company
        for company in self.branch_bulk_manager._create_queues['business_register.Company']:
            company_create_dict[company.hash_code] = company

        self.bulk_manager._create_queues['business_register.Assignee'] = []
        self.bulk_manager._create_queues['business_register.FounderFull'] = []
        self.bulk_manager._create_queues['business_register.BancruptcyReadjustment'] = []
        self.bulk_manager._create_queues['business_register.CompanyDetail'] = []
        self.bulk_manager._create_queues['business_register.CompanyToKved'] = []
        self.bulk_manager._create_queues['business_register.ExchangeDataCompany'] = []
        self.bulk_manager._create_queues['business_register.CompanyToPredecessor'] = []
        self.bulk_manager._create_queues['business_register.Signer'] = []
        self.bulk_manager._create_queues['business_register.TerminationStarted'] = []
        self.branch_bulk_manager._update_queues['business_register.Company'] = []
        self.branch_bulk_manager._create_queues['business_register.Company'] = []

        for company_to_kved in self.branch_bulk_manager._create_queues['business_register.CompanyToKved']:
            if company_to_kved.hash_code in company_update_dict:
                company_to_kved.company = company_update_dict[company_to_kved.hash_code]
            else:
                company_to_kved.company = company_create_dict[company_to_kved.hash_code]

        for exchange_data in self.branch_bulk_manager._create_queues['business_register.ExchangeDataCompany']:
            if exchange_data.hash_code in company_update_dict:
                exchange_data.company = company_update_dict[exchange_data.hash_code]
            else:
                exchange_data.company = company_create_dict[exchange_data.hash_code]

        for signer in self.branch_bulk_manager._create_queues['business_register.Signer']:
            if signer.hash_code in company_update_dict:
                signer.company = company_update_dict[signer.hash_code]
            else:
                signer.company = company_create_dict[signer.hash_code]

        self.branch_bulk_manager._commit_create(CompanyToKved)
        self.branch_bulk_manager._commit_create(ExchangeDataCompany)
        self.branch_bulk_manager._commit_create(Signer)
        self.branch_bulk_manager._create_queues['business_register.CompanyToKved'] = []
        self.branch_bulk_manager._create_queues['business_register.ExchangeDataCompany'] = []
        self.branch_bulk_manager._create_queues['business_register.Signer'] = []
