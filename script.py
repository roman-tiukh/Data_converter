from data_ocean.services.ruo_service import RuoConverter
from data_ocean.services.ratu_service import RatuConverter
from data_ocean.services.rfop_service import RfopConverter
from data_ocean.services.kved_service import KvedConverter
from data_ocean.services.koatuu_service import KoatuuConverter

KoatuuConverter().download_file()
KvedConverter().download_file()
RatuConverter().download_file()
RuoConverter().download_file()
RfopConverter().download_file()

# KvedConverter().process()
# RatuConverter().process()
# RfopConverter().process()
# RuoConverter().process()
