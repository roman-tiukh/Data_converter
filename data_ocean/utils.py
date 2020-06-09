"""
Here we are collecting alf functions for cleaning xml records from whitespaces and /
abbreviations, splitting tag.texts and converting strings with date info to datetimes
"""
import datetime
import re


# changing to lowercase, deleting 'р.', 'м.', 'с.', 'смт.', 'смт', 'сщ.', 'с/рада.', 'сщ/рада.', /
# 'вул.' from a string
def clean_name(name):
    name = name.lower()
    return re.sub(r'р\.|м\.|с\.|смт|смт\.|сщ\.|с/рада\.|сщ/рада\.', "", name).trim()

# changing to lowercase and abbreviations to full forms like 'р-н' to 'район' /
# (see all cases in short_to_full_dict)
def change_to_full_name(name):
    #a dictionary for storing all abbreviations and full forms
    short_to_full_dict = {
        'р-н': 'район',
        'вул.': 'вулиця ',
        'бульв.': 'бульвар ',
        'просп.': 'проспект ',
        'пров.': 'провулок ',
        'пл.': 'площа ',
        'обл.': 'область',
        'области': 'області'
    }
    name = name.lower()
    return name.replace(name, short_to_full_dict[name])

# extracting the first word
def get_first_word(string):
    return string.split()[0]

# extracting all words except first
def cut_first_word(string):
    words_after_first = string.split()[1:]
    return " ".join(words_after_first)

# deleting ';' from a string, then converting it to the datetime format 'Y-m-d'
def format_date_to_yymmdd(str_ddmmyy):
    ddmmyy = str_ddmmyy.replace(";", "")
    return datetime.datetime.strptime(ddmmyy, "%d.%m.%Y").strftime("%Y-%m-%d")
