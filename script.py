from data_ocean.services.rfop_service import RfopConverter
from data_ocean.services.ruo_service import RuoConverter
from data_ocean.services.ratu_service import RatuConverter

if RatuConverter().download_file() == 0:
    if RatuConverter().unzip_file() == 0:
        RatuConverter().rename_files()
        # RatuConverter().process()

if RfopConverter().download_file() == 0:
    if RfopConverter().unzip_file() == 0:
        RfopConverter().rename_files()
        # RfopConverter().process()
        # RuoConverter().process()