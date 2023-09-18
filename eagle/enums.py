from enum import Enum


class EnumWithChoices(Enum):

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)

    @classmethod
    def values(cls):
        return tuple(i.value for i in cls)
