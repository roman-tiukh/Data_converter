import re

from data_ocean.transliteration import constants


def delete_apostrophe(match_object):
    return re.sub("['`’]", '', match_object.group())


def transliterate(string):
    string = re.sub("\w['`’]\w", delete_apostrophe, string)
    word_list = re.split('(\W|\d)', string)
    new_string = ''
    for word in word_list:
        new_word = ''
        for char in word:
            if word.index(char) == 0:
                new_word += constants.UKR_TO_EN_FIRST_LETTER.get(char, constants.UKR_TO_EN.get(char, char))
            else:
                new_word += constants.UKR_TO_EN.get(char, char)
        new_word = new_word.title() if word.istitle() else new_word
        new_word = new_word.upper() if word.isupper() else new_word
        new_string += new_word
    return new_string


def replace_translated(string, search_pattern, translating_dict):
    lower_string = string.lower()
    for key in translating_dict.keys():
        key_search_pattern = re.sub('%s', key, search_pattern)
        match = re.search(key_search_pattern, lower_string)
        if match:
            existing_record = string[match.start():match.end()]
            translated_record = re.sub(key, translating_dict[key], match[0])
            if existing_record.isupper():
                translated_record = translated_record.upper()
            elif existing_record.istitle():
                translated_record = translated_record.title()
            elif existing_record[0].isupper() and existing_record[1].islower():
                translated_record = translated_record.capitalize()
            return re.sub(existing_record, translated_record, string)
    return string


def translate_company_type_in_string(string):
    return replace_translated(
        string=string,
        search_pattern="%s",  # search anywhere in string
        translating_dict=constants.COMPANY_TYPES
    )


def translate_country_in_string(string):
    return replace_translated(
        string=string,
        search_pattern="\A%s|%s\Z|, %s",  # search only at the beginning and/or at the end of string, and after ', '
        translating_dict=constants.COUNTRIES
    )
