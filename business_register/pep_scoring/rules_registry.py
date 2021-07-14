from enum import Enum, unique


@unique
class ScoringRuleEnum(Enum):
    PEP01 = 'PEP01'
    PEP02 = 'PEP02'
    PEP03_home = 'PEP03_home'
    PEP03_land = 'PEP03_land'
    PEP03_car = 'PEP03_car'
    PEP04_adr = 'PEP04_adr'
    PEP04_reg = 'PEP04_reg'
    PEP05 = 'PEP05'
    PEP07 = 'PEP07'
    PEP09 = 'PEP09'
    PEP10 = 'PEP10'
    PEP11 = 'PEP11'
    PEP13 = 'PEP13'
    PEP15 = 'PEP15'
    PEP16 = 'PEP16'
    PEP17 = 'PEP17'
    PEP18 = 'PEP18'
    PEP19 = 'PEP19'
    PEP20 = 'PEP20'
    PEP21 = 'PEP21'
    PEP22 = 'PEP22'
    PEP23 = 'PEP23'
    PEP24 = 'PEP24'
    PEP25 = 'PEP25'
    PEP26 = 'PEP26'
    PEP27 = 'PEP27'


ALL_RULES = {}


def register_rule(rule_class):
    global ALL_RULES
    ALL_RULES[rule_class.rule_id.value] = rule_class
    all_rules_copy = ALL_RULES.copy()
    ALL_RULES.clear()
    ALL_RULES.update({
        rule.rule_id.value: rule for rule in sorted(
            all_rules_copy.values(), key=lambda rule: rule.priority
        )
    })
    return rule_class
