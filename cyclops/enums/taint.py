from enum import StrEnum

class Taint(StrEnum):
    UNTRUSTED = "untrusted"
    SENSITIVE = "sensitive"
    NORMAL = "normal"
