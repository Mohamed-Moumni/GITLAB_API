# -*- coding: utf-8 -*-

import calendar
import unicodedata
from datetime import datetime
from appdirs import unicode
from odoo import fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval as seval


def fiscal_year_for(contract_date, current_date, num=0, odoo=None):
    if current_date < contract_date:
        raise UserError(odoo._(f"La date {current_date} doit être supérieur à {contract_date}"))
    dt_start = fields.Date.from_string(contract_date)
    #     print contract_date
    #     print current_date
    dt_stop = dt_start + relativedelta(years=1, days=-1)
    dt_current = fields.Date.from_string(current_date)
    while True:
        if dt_start <= dt_current <= dt_stop:
            return fields.Date.to_string(dt_start + relativedelta(years=num)), fields.Date.to_string(
                dt_stop + relativedelta(years=num))
        dt_start = dt_start + relativedelta(years=1)
        dt_stop = dt_stop + relativedelta(years=1)


def remove_accent(s_rem):
    if isinstance(s_rem, str):
        s_rem = s_rem.decode('utf8')
    return unicodedata.normalize('NFKD', s_rem).encode('ascii', 'ignore')


def to_float(text, odoo=None):
    try:
        text = str(text).strip()
    except Exception as exe:
        raise UserError(odoo._(f"Error occurred while converting {text} to float: {exe}")) from exe
    if not text:
        return 0.0
    text = text.replace(',', '.').replace(';', '.').replace(' ', '')
    text = ''.join([x for x in text if x.isdigit() or x in ['.', '-', '+']])
    try:
        return float(seval(text))
    except Exception as exe:
        raise UserError(odoo._(f"Error occurred while converting {text} to float: {exe}")) from exe


def date_range(string):
    if isinstance(string, datetime):
        string = fields.Datetime.to_string(string)
    year, month = int(string[:4]), int(string[5:7])
    part1 = string[:8]
    day = str(calendar.monthrange(year, month)[1])
    return part1 + '01', part1 + day


def normalize(champs1, champs2):
    if not champs1 and not champs2:
        return ''
    if not champs1:
        return champs2
    if not champs2:
        return champs1
    if isinstance(champs1, str):
        champs1 = unicode(champs1, 'utf-8')
    if isinstance(champs2, str):
        champs2 = unicode(champs2, 'utf-8')
    if len(champs1) > len(champs2):
        return champs1
    champs2 = champs2[:(len(champs2) - len(champs1)) / 2]
    res = champs2 + champs1 + champs2
    return res


def floattotime(value):
    if not value:
        return ''
    f_float = str(float(value)).split('.')
    n_float = int(f_float[0])
    m_float = float(f_float[1])
    m_float = m_float * 3. / 5
    m_float = int(m_float)
    return f'{n_float:0>2}:{m_float:0<2}'


def to_percent(value, is_tva=True):
    # """
    # @param : value (integer, float, long)
    # @param : is_tva (default is TRue to retuen Ex if value = 0)
    # return value %
    # """
    assert isinstance(value, (int, float)), "This function accept numbers"
    value = f"{value * 100:.2f}"
    if is_tva and value == 0.0:
        return 'Ex'
    value = value.rstrip('0').rstrip('.')
    return str(value) + ' %'


def tradd(num):
    global t1, t2
    chaine = ''
    if num == 0:
        chaine = ''
    elif num < 20:
        chaine = t1[num]
    elif num >= 20:
        if (70 <= num <= 79) or (num >= 90):
            zit = int(num / 10) - 1
        else:
            zit = int(num / 10)
        chaine = t2[zit]
        num = num - zit * 10
        if (num in (1, 11)) and zit < 8:
            chaine = chaine + ' et'
        if num > 0:
            chaine = chaine + ' ' + tradd(num)
        else:
            chaine = chaine + tradd(num)
    return chaine


def tradn(num):
    global t1, t2
    chaine = ''
    flagcent = False
    if num >= 1000000000:
        zum = int(num / 1000000000)
        chaine = chaine + tradn(zum) + ' milliard'
        if zum > 1:
            chaine = chaine + 's'
        num = num - zum * 1000000000
    if num >= 1000000:
        zum = int(num / 1000000)
        chaine = chaine + tradn(zum) + ' million'
        if zum > 1:
            chaine = chaine + 's'
        num = num - zum * 1000000
    if num >= 1000:
        if num >= 100000:
            zum = int(num / 100000)
            if zum > 1:
                chaine = chaine + ' ' + tradd(zum)
            chaine = chaine + ' cent'
            flagcent = True
            num = num - zum * 100000
            if int(num / 1000) == 0 and zum > 1:
                chaine = chaine + 's'
        if num >= 1000:
            zum = int(num / 1000)
            if (zum == 1 and flagcent) or zum > 1:
                chaine = chaine + ' ' + tradd(zum)
            num = num - zum * 1000
        chaine = chaine + ' mille'
    if num >= 100:
        zum = int(num / 100)
        if zum > 1:
            chaine = chaine + ' ' + tradd(zum)
        chaine = chaine + " cent"
        num = num - zum * 100
        if num == 0 and zum > 1:
            chaine = chaine + 's'
    if num > 0:
        chaine = chaine + " " + tradd(num)
    return chaine


def trad(number, unite, decim, custom, base):
    unites, decims = '', ''
    if unite:
        unites = unite.lower().endswith('s') and unite or (unite + 's')
    if decim:
        decims = decim.lower().endswith('s') and decim or (decim + 's')
    global t1, t2
    number = round(number, 2)
    t1 = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
          "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
    t2 = ["", "dix", "vingt", "trente", "quarante", "cinquante",
          "soixante", "septante", "quatre-vingt", "nonante"]
    z1 = int(number)
    z3 = ((number - z1) * 100) * base / 100.
    z2 = int(round(z3, 0))
    demi = custom and str(z2).startswith('5') and str(z2).replace('0', '') == '5' and True or False
    if z1 == 0:
        chaine = "zéro"
    else:
        chaine = tradn(abs(z1))
    if z1 > 1 or z1 < -1:
        if unite != '':
            chaine = chaine + " " + unites
    else:
        chaine = chaine + " " + unite
    if z2 > 0:
        if demi:
            chaine = chaine + " et demi"
        else:
            chaine = chaine + tradn(z2)
        if z2 > 1 or z2 < -1:
            if decim != '' and not demi:
                chaine = chaine + " " + decims
        else:
            if not demi:
                chaine = chaine + " " + decim
    if number < 0:
        chaine = "moins " + chaine
    return chaine


def convert_txt2amount(number, unite="DH", decim="centime", custom=False, base=100):
    return trad(number, unite, decim, custom, base).strip().capitalize()
