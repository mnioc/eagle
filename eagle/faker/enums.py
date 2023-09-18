from eagle.enums import EnumWithChoices


class FieldType(EnumWithChoices):

    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    FLOAT = 'float'
    CHAR = 'char'
    TEXT = 'text'
    LIST = 'list'
    DICT = 'dict'
    CHOICES = 'choices'


class InvalidProviderType(EnumWithChoices):

    MISSING_REQUIRE = 'missing_require'
    EXCEED_MAX_VALUE = 'exceed_max_value'
    EXCEED_MIN_VALUE = 'exceed_min_value'
    INVALID_CHOICE = 'invalid_choice'
    INVALID_TYPE = 'invalid_type'
    NULL = 'null'
    BLANK = 'blank'
    EXCEED_MAX_LENGTH = 'exceed_max_length'
    EXCEED_MIN_LENGTH = 'exceed_min_length'
    INVALID_DICT = 'invalid_dict'
