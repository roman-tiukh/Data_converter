from business_register.models.company_models import FounderFull


class Link:

    def __init__(self, source, target):
        self.source = source
        self.target = target


class PepAssetsSearcher:

    def __init__(self):
        self.nodes = []
        self.links = []

    def find_pep_companies(self, pep_name):
        # TODO: retreive a public person object from another DB
        pep = pep_name
        self.nodes.append(pep)
        founder_of = FounderFull.objects.filter(name=pep_name)
        if not founder_of:
            return 'no companies are founded by this person'
        for founder in founder_of:
            self.nodes.append(founder.company)
            self.links.append(Link(pep, founder.company.id))
            self.find_founded_companies(founder.company)
        print(f'There are {len(self.nodes) - 1} companies linked with this person')
        return self.nodes, self.links

    def find_founded_companies(self, company):
        founder_of = FounderFull.objects.filter(edrpou=company.edrpou)
        if not founder_of:
            return 'no other companies are founded by these companies'
        for founder in founder_of:
            self.nodes.append(founder.company)
            self.links.append(Link(company.id, founder.company.id))
            self.find_founded_companies(founder.company)
