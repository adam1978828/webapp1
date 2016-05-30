__author__ = 'D.Kalpakchi'


def convert2camelCase(name):
    return "".join([chunk.capitalize() if i != 0 else chunk for i, chunk in enumerate(name.split('_'))])


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(string)
        return True
    except (TypeError, ValueError):
        pass
    return False


def remove_multilingual_words(text):
    if isinstance(text, basestring):
        return text.replace('BC', '').replace('AD', '')
    else:
        raise ValueError('Given value is not string')


def filter_chars(value, string):
    if isinstance(value, str):
        return value.translate(None, string)
    elif isinstance(value, unicode):
        char_map = dict.fromkeys(map(ord, string), None)
        return value.translate(char_map) or value
    else:
        raise ValueError('Given value is not string')


def is_integer(string):
    try:
        int_val = int(string)
        return True
    except ValueError:
        pass
    return False


def is_float(string):
    try:
        int_val = float(string)
        return True
    except ValueError:
        pass
    return False


def is_gt_zero(string):
    try:
        float_val = float(string)
        if float_val > 0:
            return True
    except ValueError:
        pass
    return False


def is_enough(string):
    try:
        int_val = int(float(string) * 100)
        if int_val > 0:
            return True
    except ValueError:
        pass
    return False


def is_in_range_1_to_100(string):
    try:
        int_val = int(string)
        if 0 < int_val <= 100:
            return True
    except ValueError:
        pass
    return False


def is_2_digits_after_point(string):
    try:
        float_val_list = string.split('.')
        if len(float_val_list) > 1:
            if len(float_val_list[1]) > 2:
                return False
        return True
    except ValueError:
        pass
    return False

def is_gt_or_eq_zero(string):
    try:
        float_val = float(string)
        if float_val >= 0:
            return True
    except ValueError:
        pass
    return False

def is_integer_limit(string, integer):
    try:
        float_val = float(string)
        int_val = int(float_val)
        if len(str(int_val)) <= integer:
            return True
    except ValueError:
        pass
    return False

def is_fractional_limit(string, fractional):
    try:
        float_val = float(string)
        if len(str(float_val).split('.')[1]) <= fractional:
            return True
    except ValueError:
        pass
    return False