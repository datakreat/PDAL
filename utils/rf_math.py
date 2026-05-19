import math


def linear_to_db(value):

    return 10 * math.log10(value)


def db_to_linear(value):

    return 10 ** (value / 10)