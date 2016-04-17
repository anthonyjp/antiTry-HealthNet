import re


def is_camel_case(s):
    """
    Checks if a string is in camel case, since this has many variations all it does is check if a string is
    neither totally uppercase nor totally lowercase.

    :param s: String to check
    :return: True if not lowercase or uppercase, false otherwise
    """
    return not s.islower() and not s.isupper()


def camelcase_to_snakecase(s):
    """
    Takes a CamelCase string and converts it to snake_case.

    HealthNet -> health_net
    HNLogEntry -> hn_log_entry
    HealthNeT -> health_ne_t
    HealthNeTTT -> health_ne_ttt

    :param s: Text to convert to snake_case
    :return: The string in snake_case, unless the string was not CamelCase, then the string is returned
    """

    if not is_camel_case(s):
        return s

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def camelcase_to_slug(s):
    """
    Takes a CamelCase and converts it to wonderful-slug-case.

    HealthNet -> Health-Net
    HNLogEntry -> HNLog-Entry
    HealthNeT -> Health-Ne-T
    HealthNeTTT -> Health-Ne-TTT

    :param s: Text to convert to slug-case
    :return: The string converted to slug-case, or the string itself if the string was not in CamelCase
    """

    if not is_camel_case(s):
        return s

    # Fill Result up to last character
    res = s[0]
    for i in range(1, len(s) - 1):
        c = s[i]
        lastc = res[-1:]

        # If the current character is uppercase and the next character is not uppercase
        # and the last character was alphabetic then add a '-'
        if c.isupper() and not s[i + 1].isupper() and lastc.isalpha():
            res += '-'

        res += c

    # Find farthest consecutive capital letter from the end (count until a lowercase is found
    ires = -1
    i = 1
    while 0 < i < len(res):
        if i == 1 and not res[-i:].isupper():
            ires = i
            break
        elif i != 1 and not res[-i:-i + 1].isupper():
            ires = i - 1
            break
        else:
            i += 1

    if ires > 0 and res[-ires - 1:].isalpha() and (
        (ires == 1 and res[-ires:].isupper()) or res[-ires:-ires + 1].isupper()):
        res = res[:-ires] + '-' + res[-ires:]
    elif ires == 1 and s[-1:].isupper() and res[-1].isalpha():
        res += '-'

    res += s[-1:]

    return res
