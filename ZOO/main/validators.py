import re
from django.core.exceptions import ValidationError


def phone_validator(phone_number):
    regular = r'(\+375)?(?:33|44|25|29)?([0-9]{7})'
    if re.fullmatch(regular, phone_number):
        return phone_number
    else:
        raise ValidationError('Неправильный номер телефона')


def name_validator(name):
    print(name)
    regular = r'^([А-Я]{1}[а-яё]{1,30}|[A-Z]{1}[a-z]{1,30})$'
    if re.fullmatch(regular, name):
        return name
    else:
        raise ValidationError('Неверное имя!!!')