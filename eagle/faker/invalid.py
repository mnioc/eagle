import copy
from collections import namedtuple
from eagle.faker.enums import InvalidProviderType
from eagle.utils import generate_random_string


class InvalidValue(namedtuple('InvalidValue', ['value', 'type'])):
    __slots__ = ()


class InvalidDictValue(namedtuple('InvalidValue', ['value', 'type', 'sub_field'])):
    __slots__ = ()


class InvalidValueProvider:
    """A value provider that always returns an invalid value."""

    # from eagle.faker.fields import Field

    @classmethod
    def get_null_value(cls, field=None):
        return InvalidValue(None, InvalidProviderType.NULL.value)

    @classmethod
    def get_blank_value(cls, field=None):
        return InvalidValue('', InvalidProviderType.BLANK.value)

    @classmethod
    def get_invalid_choice_value(cls, field):
        assert field.choices is not None, "Field must have choices"
        while True:
            random_string = generate_random_string()
            if random_string not in field.choices:
                return InvalidValue(random_string, InvalidProviderType.INVALID_CHOICE.value)

    @classmethod
    def get_invalid_type_value(cls, field):
        pass

    @classmethod
    def get_invalid_max_length_value(cls, field):
        assert field.max_length is not None, "Field must have max_length"
        value = generate_random_string(field.max_length + 1)
        return InvalidValue(value, InvalidProviderType.EXCEED_MAX_LENGTH.value)

    @classmethod
    def get_invalid_min_length_value(cls, field):
        assert field.min_length is not None, "Field must have min_length"
        value = generate_random_string(field.min_length - 1)
        return InvalidValue(value, InvalidProviderType.EXCEED_MIN_LENGTH.value)

    @classmethod
    def get_invalid_max_value_value(cls, field):
        assert field.max_value is not None, "Field must have max_value"
        value = field.max_value + 1
        return InvalidValue(value, InvalidProviderType.EXCEED_MAX_VALUE.value)

    @classmethod
    def get_invalid_min_value_value(cls, field):
        assert field.min_value is not None, "Field must have min_value"
        value = field.min_value - 1
        return InvalidValue(value, InvalidProviderType.EXCEED_MIN_VALUE.value)

    @classmethod
    def get_invalid_dict_value(cls, field):
        values = []

        for field_name, field_instance in field.fields.items():

            if field_instance.required:
                valid_value_copy = copy.deepcopy(field.generate_valid_value())
                del valid_value_copy[field_name]
                values.append(
                    InvalidDictValue(
                        value=valid_value_copy,
                        type=InvalidProviderType.MISSING_REQUIRE,
                        sub_field=field_name
                    )
                )

            for invalid_value in field_instance.generate_invalid_values():
                valid_value_copy = copy.deepcopy(field.generate_valid_value())
                valid_value_copy[field_name] = invalid_value.value
                values.append(
                    InvalidDictValue(
                        value=valid_value_copy,
                        type=invalid_value.type,
                        sub_field=field_name
                    )
                )

        return values
