from constants.constants import null_values, true_values, false_values


def pars_null(value: str | int | float | bool | None = None):
    if type(value) is int or type(value) is float or type(value) is bool:
        return value

    elif value in true_values:
        return True

    elif value in false_values:
        return False

    elif value is None or value in null_values or value == '':
        return None

    return value
