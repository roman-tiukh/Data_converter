from business_register.pep_scoring.constants import ScoringRuleEnum

"""
Messages for scoring rules, it uses ".format()" method for insert data into a message.
See usage in PepScoring.get_message_for_locale method.
"""
SCORING_MESSAGES = {
    ScoringRuleEnum.PEP01.value: {
        'uk': 'У декларації про майно не вказано дружину та/або дітей PEP, '
              'тоді як реєстр pep.org.ua містить інформацію про них',
        'en': 'Asset declaration does not indicate PEP\'s wife and/or children, '
              'while pep.org.ua register has information on them',
    },
    ScoringRuleEnum.PEP18.value: {
        'uk': 'кількість люксових авто - {amount_of_luxury_cars}',
        'en': 'amount of luxury cars - {amount_of_luxury_cars}',
    },
}
