import copy
import random
from typing import List, Union, Callable, Any
from functools import singledispatch


@singledispatch
def get_dict_value(key, data) -> Any:
    ...


@get_dict_value.register(str)
def _str_key(key: str, data: dict) -> Any:  # noqa
    return data.get(key)


@get_dict_value.register(list)
def _list_key(key: list, data: dict) -> Any:  # noqa
    for k in key:
        data = data.get(k)
    return data


@singledispatch
def set_dict_value(key, data, value) -> None:
    ...


@set_dict_value.register(str)
def _str_key(key: str, data: dict, value) -> None:  # noqa
    data[key] = value


@set_dict_value.register(list)
def _list_key(key: list, data: dict, value) -> None:  # noqa
    for k in key[:-1]:
        data = data.setdefault(k, {})
    data[key[-1]] = value


@singledispatch
def key_exist(key, data) -> bool:
    ...


@key_exist.register(str)
def _str_key(key: str, data: dict) -> bool:  # noqa
    return key in data


@key_exist.register(list)
def _list_key(key: list, data: dict) -> bool:  # noqa
    for k in key:
        if k not in data:
            return False
        data = data.get(k)
    return True


class BaseDictValue:

    def __init__(self, key: Union[str, List[str]]) -> None:
        self.key = key

    def _get_value(self, data):
        return get_dict_value(self.key, data)

    def _set_value(self, data, value):
        set_dict_value(self.key, data, value)

    def _key_exist(self, data):
        return key_exist(self.key, data)

    def get_whold_key(self):
        return self.key if isinstance(self.key, str) else '.'.join(self.key)

    def get_repr_condition(self):
        return self.key

    def delete(self, data):
        if isinstance(self.key, str):
            del data[self.key]
        else:
            to_delete_key = self.key[-1]
            for key in self.key:
                if key == to_delete_key:
                    break
                data = data.get(key)
            del data[to_delete_key]


class DictValueEqual(BaseDictValue):

    def __init__(self, expected, *args, **kwargs):
        self.expected = expected
        super().__init__(*args, **kwargs)

    def check(self, data):
        return self._get_value(data) == self.expected

    def set_valid_value(self, data):
        self._set_value(data, self.expected)

    def get_repr_condition(self):
        return f'{self.key}=={self.expected}'


class DictValueIn(BaseDictValue):

    def __init__(self, expecteds, *args, **kwargs):
        self.expecteds = expecteds
        super().__init__(*args, **kwargs)

    def check(self, data):
        return self._get_value(data) in self.expecteds

    def set_valid_value(self, data):
        self._set_value(data, random.choice(self.expecteds))

    def get_repr_condition(self):
        return f'{self.key} in {self.expecteds}'


class DictKeyExist(BaseDictValue):

    def __init__(self, default, *args, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def check(self, data):
        return self._key_exist(data)

    def set_valid_value(self, data):
        self._set_value(data, self.default)

    def get_repr_condition(self):
        return f'{self.key} exist'

    def generate_invalid_data(self, data, condition: BaseDictValue):
        from eagle.faker.bases import InvalidData
        invalid_data = copy.deepcopy(data)
        self.delete(invalid_data)
        return InvalidData(
            data=invalid_data,
            field_name=self.get_whold_key(),
            invalid_reason=f'( missing_require  | where {condition.get_repr_condition()})',
            whold_field=self.get_whold_key(),
        )

class DictKeyDoesNotExist(BaseDictValue):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check(self, data):
        return not self._key_exist(data)

    def set_valid_value(self, data):
        self.delete(data)

    def get_repr_condition(self):
        return f'{self.key} does not exist'

    def generate_invalid_data(self, data, condition: BaseDictValue):
        from eagle.faker.bases import InvalidData
        invalid_data = copy.deepcopy(data)
        self._set_value(invalid_data, None)
        return InvalidData(
            data=invalid_data,
            field_name=self.get_whold_key(),
            invalid_reason=f'( null | where {condition.get_repr_condition()} )',
            whold_field=self.get_whold_key(),
        )


class DictValueNotNull(BaseDictValue):

    def __init__(self, default, *args, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def check(self, data):
        return self._get_value(data) is not None

    def set_valid_value(self, data):
        self._set_value(data, self.default)

    def get_repr_condition(self):
        return f'{self.key} not null'

    def generate_invalid_data(self, data, condition: BaseDictValue):
        from eagle.faker.bases import InvalidData
        invalid_data = copy.deepcopy(data)
        self._set_value(invalid_data, None)
        return InvalidData(
            data=invalid_data,
            field_name=self.get_whold_key(),
            invalid_reason=f'( null | where {condition.get_repr_condition()} )',
            whold_field=self.get_whold_key(),
        )


class RelationConstraint:

    def __init__(self, condition: BaseDictValue, constraints: List[BaseDictValue]) -> None:
        self.condition = condition
        self.constraints = constraints
