import abc
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Type
import random
import string
from eagle.faker.enums import FieldType
from eagle.faker.invalid import InvalidValueProvider, InvalidValue


class Field:

    field_type: Union[None, FieldType] = None

    def __init__(
        self,
        required=False,
        default=None,
        allow_null=True,
        generate_invalid_func: Optional[Callable] = None,
        invalid_values: Optional[List[InvalidValue]] = None,
        disable_default_invalid_provider=False,
        valid_value: Optional[Any] = None,
    ):
        """
        Args:
            required (bool): Whether the field is required.
            default (Any): Default value for the field.
            allow_null (bool): Whether the field can be null.
            generate_invalid_func (Callable): Function to generate invalid values.
                It should accept a field as the only argument and return a list of `InvalidValue`.
                e.g.
                    >>> def custom_generate_invalid_values(field: Field):
                            return [
                                InvalidValue('invalid_value', 'custom_invalid_type')
                            ]
                    >>> name = Field(required=True, generate_invalid_func=custom_generate_invalid_values)
        """
        self.required = required
        self.default = default
        self.allow_null = allow_null

        self.disable_default_invalid_provider = disable_default_invalid_provider

        # NOTE
        # that the ultimately returned invalid value will be a collection of the following:
        #     1. `generate_invalid_func`
        #     2. `invalid_values`
        #     3. `default_invalid_providers`
        # unless you explicitly disable the default value
        self.generate_invalid_func = generate_invalid_func
        self.invalid_values = invalid_values
        self._default_invalid_providers = []

        if not self.allow_null:
            self.register_invalid_provider(InvalidValueProvider.get_null_value)
        
        self.valid_value = valid_value

    def register_invalid_provider(self, provider):
        """
        Register a custom invalid value provider.
        """

        if self.disable_default_invalid_provider:
            return

        if provider not in self._default_invalid_providers:
            self._default_invalid_providers.append(
                provider
            )

    def generate_valid_value(self):
        """
        Generate valid data.
        """
        raise NotImplementedError(
            'You must implement the generate_valid_value() method.'
        )

    def generate_default_invalid_values(self):
        ret = []
        for invalid_provider_func in self._default_invalid_providers:
            invalid = invalid_provider_func(self)
            if isinstance(invalid, list):
                ret.extend(invalid)
            else:
                ret.append(invalid)
        return ret

    def generate_invalid_values(self):
        invalid_values = []

        if self.invalid_values:
            invalid_values += list(self.invalid_values)

        if self.generate_invalid_func:
            assert callable(self.generate_invalid_func), ('generate_invalid_func must be callable.')
            invalid_values += self.generate_invalid_func(self)

        invalid_values += self.generate_default_invalid_values()

        return invalid_values


class BooleanField(Field):

    field_type = FieldType.BOOLEAN.value

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        return random.choice([True, False])


class CharField(Field):

    field_type = FieldType.CHAR.value

    def __init__(
        self,
        max_length: Optional[int] = 20,
        min_length: Optional[int] = 1,
        allow_blank: bool = True,
        allow_strings: Optional[Union[List[str], str]] = None,
        prefix: str = '',
        suffix: str = '',
        *args,
        **kwargs
    ):
        """
        Generates a random string of upper and lowercase letters.
        Args:
            max_length (int): Maximum length of the string.
            min_length (int): Minimum length of the string.
            allow_blank (bool): Whether the string can be blank.
            allow_strings (list): List of strings to allow.
                options:
                    - '*': Allow any char.
                    - 'whitespace': Allow '\t\n\r\v\f'.
                    - 'ascii_lowercase': Allow 'abcdefghijklmnopqrstuvwxyz'.
                    - 'ascii_uppercase': Allow 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.
                    - 'ascii_letters': Allow 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.
                    - 'digits': Allow '0123456789'.
                    - 'hexdigits': Allow '0123456789abcdefABCDEF'.
                    - 'octdigits': Allow '01234567'.
                    - 'punctuation': Allow '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'.
                if allow_strings is None, allow_strings will be set to ['*'].
            prefix (str): Prefix to add to the string.
            suffix (str): Suffix to add to the string.
        """
        super().__init__(*args, **kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.allow_blank = allow_blank

        assert self.max_length >= self.min_length, "Maximum length must be greater than or equal to minimum length"

        self.prefix = prefix
        self.suffix = suffix

        self.allow_strings = allow_strings
        if (
            self.allow_strings is None
            or self.allow_strings == '*'
            or self.allow_strings == ['*']
        ):
            self.allow_strings = [
                'ascii_letters', 'digits',
            ]

        if not self.allow_blank:
            self.register_invalid_provider(InvalidValueProvider.get_blank_value)

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        allow_strings = ''.join(
            getattr(string, allow_string) for allow_string in self.allow_strings
        )
        random_length = random.randint(1, 20)
        random_string = ''.join(random.choice(allow_strings) for _ in range(random_length))
        random_string = self.prefix + random_string + self.suffix
        if self.allow_blank:
            random_string = random.choice([random_string, ''])
        return random_string


class IntegerField(Field):

    field_type = FieldType.INTEGER.value

    def __init__(
        self,
        max_value: Optional[int] = None,
        min_value: Optional[int] = None,
        *args,
        **kwargs
    ):
        """
        Generates a random integer.
        Args:
            max_value (int): Maximum value of the integer.
            min_value (int): Minimum value of the integer.
        """
        super().__init__(*args, **kwargs)
        self.max_value = max_value
        self.min_value = min_value

        if self.max_value:
            self.register_invalid_provider(InvalidValueProvider.get_invalid_max_value_value)

        if self.min_value:
            self.register_invalid_provider(InvalidValueProvider.get_invalid_min_value_value)

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        min_value = self.min_value
        if self.min_value is None:
            min_value = -1000
        max_value = self.max_value
        if self.max_value is None:
            max_value = 1000

        assert max_value >= min_value, "Maximum value must be greater than or equal to minimum value"
        return random.randint(min_value, max_value)


class ChoiceField(Field):

    field_type = FieldType.CHOICES.value

    def __init__(
        self,
        choices: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
        allow_blank: bool = True,
        *args,
        **kwargs
    ):
        """
        Generates a random choice.
        Args:
            choices (list): List of choices.
        """
        super().__init__(*args, **kwargs)
        self.choices = choices or []
        self.allow_blank = allow_blank

        if self.choices:
            self.register_invalid_provider(InvalidValueProvider.get_invalid_choice_value)

        if not self.allow_blank:
            self.register_invalid_provider(InvalidValueProvider.get_blank_value)

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        return random.choice(self.choices)


class FloatField(IntegerField):

    field_type = FieldType.FLOAT.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        min_value = self.min_value
        if self.min_value is None:
            min_value = -1000
        max_value = self.max_value
        if self.max_value is None:
            max_value = 1000

        assert max_value >= min_value, "Maximum value must be greater than or equal to minimum value"
        return round(random.uniform(min_value, max_value), 2)


class DictField(Field):

    field_type = FieldType.DICT.value

    def __init__(self, *args, **kwargs):
        """
        Args:
            fields (dict): Dictionary of fields.
        """

        # Collect sub fields from kwargs.
        super_signature = inspect.signature(super().__init__)
        super_params = super_signature.parameters.keys()
        kwargs_keys = list(kwargs.keys())
        fields = {
            key: kwargs.pop(key)
            for key in kwargs_keys
            if key not in super_params and isinstance(kwargs[key], Field)
        }
        super().__init__(*args, **kwargs)

        self.fields = fields
        self.register_invalid_provider(InvalidValueProvider.get_invalid_dict_value)

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        return {
            field_name: field_instance.generate_valid_value()
            for field_name, field_instance in self.fields.items()
        }


class ListField(Field):

    field_type = FieldType.LIST.value

    def __init__(
        self,
        fields: Optional[List[Field]] = None,
        length: Optional[int] = None,
        min_length: Optional[int] = 1,
        max_length: Optional[int] = 10,
        *args,
        **kwargs
    ):
        """
        Generates a random list.
        Args:
            fields (list): List of fields.
            length (int): Length of the list.
            min_length (int): Minimum length of the list.
            max_length (int): Maximum length of the list.
        """
        super().__init__(*args, **kwargs)
        self.fields = fields or []
        self.length = length
        self.min_length = min_length
        self.max_length = max_length

        assert self.max_length >= self.min_length, "Maximum length must be greater than or equal to minimum length"

    def generate_valid_value(self):
        if self.valid_value is not None:
            return self.valid_value
        random_length = self.length or random.randint(self.min_length, self.max_length)
        return [
            field.generate_valid_value()
            for field in self.fields
        ][:random_length]
