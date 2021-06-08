# django-simple-history history_type: + for create, ~ for update, and - for delete
class HistoryTypes:
    CREATE = '+'
    UPDATE = '~'
    DELETE = '-'


KVED_SECTIONS = {
    "not_valid": "not_valid",
    "сільське господарство, лісове господарство та рибне господарство": "agriculture, forestry and fishing",
    "добувна промисловість і розроблення кар'єрів": "mining and quarrying",
    "переробна промисловість": "manufacturing",
    "постачання електроенергії, газу, пари та кондиційованого повітря":
        "electricity, gas, steam and air conditioning supply",
    "водопостачання; каналізація, поводження з відходами": "water supply; sewerage; waste management and remediation",
    "будівництво": "construction",
    "оптова та роздрібна торгівля; ремонт автотранспортних засобів і мотоциклів":
        "wholesale and retail trade; repair of motor vehicles and motorcycles",
    "транспорт, складське господарство, поштова та кур'єрська діяльність":
        "warehousing and support activities for transportation, postal and courier activities",
    "тимчасове розміщування й організація харчування": "accommodation and food service activities",
    "інформація та телекомунікації": "information and communication",
    "фінансова та страхова діяльність": "financial and insurance activities",
    "операції з нерухомим майном": "real estate activities",
    "професійна, наукова та технічна діяльність": "professional, scientific and technical activities",
    "діяльність у сфері адміністративного та допоміжного обслуговування":
        "administrative and support services activities",
    "державне управління й оборона; обов'язкове соціальне страхування":
        "public administration and defence; compulsory social security",
    "освіта": "education",
    "охорона здоров'я та надання соціальної допомоги": "human health and social work activities",
    "мистецтво, спорт, розваги та відпочинок": "arts, sport, entertainment and recreation",
    "надання інших видів послуг": "other services activities",
    "діяльність домашніх господарств": "activities of households",
    "діяльність екстериторіальних організацій і органів": "activities of extraterritorial organizations and bodies"
}
