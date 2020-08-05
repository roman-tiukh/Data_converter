from .business_converter import BusinessConverter


class PepConverter(BusinessConverter):

    def save_to_db(self, json_file):
        data = self.load_json(json_file)
        for pep in data:
            print(pep.keys())
            break
