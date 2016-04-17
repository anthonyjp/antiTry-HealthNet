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

    :param s: Text to convert to slug-case
    :return: The string converted to slug-case, or the string itself if the string was not in CamelCase
    """

    if not is_camel_case(s):
        return s

    res = ''
    for i, c in enumerate(s):
        res += c if not s.isspace() else '-'

        # If character was uppercase and it is not the first or last character
        if c.isupper() and 0 < i < len(s) - 1:
            res += '-'

    return res
