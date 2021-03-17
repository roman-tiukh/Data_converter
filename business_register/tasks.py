from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def update_pep():
    print('********************')
    print('*    Update PEP    *')
    print('********************')

    from business_register.converter.pep import PepDownloader
    PepDownloader().update()

    print('*** Task update_pep is done. ***')


@shared_task
def update_fop():
    print('********************')
    print('*    Update FOP    *')
    print('********************')

    from business_register.converter.fop import FopDownloader
    FopDownloader().update()

    print('*** Task update_fop is done. ***')


@shared_task
def update_ukr_company():
    print('**********************************')
    print('*   Update UKR Company (SHORT)   *')
    print('**********************************')

    from business_register.converter.company_converters.ukr_company import UkrCompanyDownloader
    UkrCompanyDownloader().update()

    print('*** Task update_ukr_company is done. ***')


@shared_task
def update_ukr_company_full():
    print('*********************************')
    print('*   Update UKR Company (FULL)   *')
    print('*********************************')

    from business_register.converter.company_converters.ukr_company_full import UkrCompanyFullDownloader
    UkrCompanyFullDownloader().update()

    print('*** Task update_ukr_company_full is done. ***')


@shared_task
def update_uk_company():
    print('***************************')
    print('*    Update UK Company    *')
    print('***************************')

    from business_register.converter.company_converters.uk_company import UkCompanyDownloader
    UkCompanyDownloader().update()

    print('*** Task update_uk_company is done. ***')


# @shared_task
# def update_kved():
#     print('*********************')
#     print('*    Update KVED    *')
#     print('*********************')
#
#     from business_register.converter.kved import KvedDownloader
#     KvedDownloader().update()
#
#     print('*** Task update_kved is done. ***')
