
def get_class_values(obj: object, excludes: list | None = None) -> dict:
    if excludes is None:
        excludes = []
    values = dict()
    for name, value in vars(obj).items():
        if not name.startswith('__') and type(value) is not classmethod:
            if not excludes.__contains__(name):
                values[name] = value

    return values


def get_var_name(obj: object, var) -> str:
    for name, value in vars(obj).items():
        if not name.startswith('__') and type(value) is not classmethod:
            if id(var) == id(value):
                return name
