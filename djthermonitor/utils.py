from decimal import Decimal


def celsius_to_fahrenheit(temp_c_decimal):
    """
    Convert a decimal celsius temperature to fahrenheit.

    Returns an integer.
    """
    return int(Decimal(9.0 / 5.0) * Decimal(temp_c_decimal) + Decimal(32.0))
