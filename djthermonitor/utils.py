from decimal import Decimal

"""
# Convert a decimal celsius temperature to fahrenheit.
#
# Returns an integer.
"""
def celsius_to_fahrenheit(temp_c_decimal):
    return int(Decimal(9.0 / 5.0) * Decimal(temp_c_decimal) + Decimal(32.0))