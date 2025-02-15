from utils.get_class_values import get_class_values, get_var_name


class NoneAnalysis:
    def __init__(self, nones, no_nones, have_none):
        self.nones = nones
        self.no_nones = no_nones
        self.have_none = have_none


def none_analysis(obj: object, excludes: list | None = None):
    nones = []
    no_nones = []

    if excludes is None:
        excludes = []

    excludes = [
        get_var_name(obj, i) for i in excludes
    ]

    params = get_class_values(
        obj,
        excludes=excludes,
    )

    for k, v in params.items():
        if v is None:
            nones.append(k)
        else:
            no_nones.append(k)

    print(nones)
    print(no_nones)

    return NoneAnalysis(nones=nones, no_nones=no_nones, have_none=len(nones) > 0)
