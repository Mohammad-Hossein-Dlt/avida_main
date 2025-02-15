import enum

null_values = ["null", "Null", "NULL", "none", "None", "NONE"]
true_values = ["true", "True", "TRUE", "t", "T"]
false_values = ["false", "False", "FALSE", "f", "F"]


class RoleEntities(str, enum.Enum):
    assistant = "assistant"
    user = "user"
