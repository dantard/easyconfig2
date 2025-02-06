from PyQt5.QtGui import QIntValidator, QDoubleValidator


def get_validator_type(validator):
    if isinstance(validator, QIntValidator):
        return int
    elif isinstance(validator, QDoubleValidator):
        return float
    else:
        return str


def get_validator_from_type(value_type):
    if value_type == int:
        return QIntValidator()
    elif value_type == float:
        return QDoubleValidator()
    else:
        return None
