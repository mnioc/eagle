import inspect
from typing import List, Dict, Union, Any
from collections import namedtuple
from eagle.faker.fields import Field
from eagle.faker.enums import InvalidProviderType
from eagle.faker.invalid import InvalidValue, InvalidDictValue
import copy
from eagle.faker.constraint import RelationConstraint
from eagle.logger import logger
from eagle.testcase.bases import TestCaseManager


class InvalidData(namedtuple('InvalidData', ['data', 'field_name', 'invalid_reason', 'whold_field'])):
    __slots__ = ()


class RegisterFieldMetaclass(type):
    """
    This metaclass sets a dictionary named `_declared_fields` on the class.
    Any instances of `Field` included as attributes on either the class
    or on any of its superclasses will be included in the
    `_declared_fields` dictionary.
    """

    def __new__(cls, name, bases, class_attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, class_attrs, **kwargs)
        if not inspect.isabstract(new_cls):
            new_cls._declared_fields = {
                field_name: field
                for field_name, field in new_cls.__dict__.items()
                if isinstance(field, Field)
            }
        return new_cls


class Faker(metaclass=RegisterFieldMetaclass):
    """
    A generic virtual data generator class that generates valid and invalid data based on declared fields
    and handles relation constraints.

    Attributes:
        _declared_fields: A dictionary storing declared fields, mapping field names to `eagle.faker.fields.Field` objects.
        _invalid_data: A list to store generated invalid data.
        _relation_invalid_data: (List): A list to store invalid data related to relation constraints.
        _valid_data (Dict[str, Any]): A dictionary to store generated valid data.

    Properties:
        valid_data (Dict[str, Any]): Get the generated valid data. It generates data if not generated already by calling the _generate_valid_data method.
        invalid_data (List[InvalidData]): Get a list of generated invalid data, including invalid field data and data related to relation constraints.
        copy_valid_data (Dict[str, Any]): Get a deep copy of the generated valid data.
        relation_constraints (List[RelationConstraint]): Get a list of relation constraints used to handle constraints between fields.

    Usage:
        >>> from eagle.faker import Faker
        >>> from eagle.faker.fields import CharField, IntegerField
        >>> Class UserFaker(Faker):
        >>>     name = CharField(max_length=10)
        >>>     age = IntegerField(min_value=0, max_value=100)
        >>> user_faker = UserFaker()
        >>> user_faker.valid_data
        {'name': 'eagle', 'age': 20}
        >>> user_faker.invalid_data
        [InvalidData(data={'name': 'eagle', 'age': -1}, field_name='age', invalid_reason='exceed_min_value', whold_field='age')]
    """

    objects = TestCaseManager()

    _declared_fields: Dict[str, Field] = {}

    def __init__(self) -> None:
        self._invalid_data: List[InvalidData] = []
        self._relation_invalid_data = []
        self._valid_data: Dict[str, Any] = {}

    @property
    def valid_data(self) -> Dict[str, Any]:
        if not self._valid_data:
            self._valid_data = self._generate_valid_data()
        return self._valid_data

    @property
    def invalid_data(self) -> List[InvalidData]:
        if not self._invalid_data:
            self._generate_invalid_data()
        return self._invalid_data + self._relation_invalid_data

    @property
    def copy_valid_data(self) -> Dict[str, Any]:
        return copy.deepcopy(self.valid_data)

    def add_invalid_data(self, invalid_data: InvalidData) -> None:
        self._invalid_data.append(invalid_data)

    def _generate_valid_data(self) -> Dict[str, Any]:
        valid_data = {
            field_name: field.generate_valid_value()
            for field_name, field in self._declared_fields.items()
        }
        logger.info(f'Generate valid data: {valid_data}')
        valid_data = self.check_relation_constraint(valid_data)
        return valid_data

    def check_relation_constraint(self, valid_data) -> bool:
        for relation_constraint in self.relation_constraints:
            condition = relation_constraint.condition

            # If condition is not satisfied
            # then skip this relation constraint
            if not condition.check(valid_data):
                continue

            logger.info(f'Condition: {condition.get_repr_condition()} is True')

            for constraint in relation_constraint.constraints:

                # If constraint is satisfied
                # then set valid value for constraint
                if not constraint.check(valid_data):
                    logger.info(f'Constraint {constraint.get_repr_condition()} is False. change valid value.')
                    constraint.set_valid_value(valid_data)

                # Generate invalid data
                valid_data = copy.deepcopy(valid_data)
                self._relation_invalid_data.append(
                    constraint.generate_invalid_data(valid_data, condition)
                )
                logger.info(f'Generate invalid data for constraint {constraint.get_repr_condition()}')

        return valid_data

    def _generate_missing_required_data(self, field_name: str) -> InvalidData:
        missing_require_data = self.copy_valid_data
        del missing_require_data[field_name]
        self.add_invalid_data(
            InvalidData(
                data=missing_require_data,
                field_name=field_name,
                invalid_reason=InvalidProviderType.MISSING_REQUIRE.value,
                whold_field=field_name
            )
        )

    def _generate_invalid_data(self) -> List[InvalidData]:
        for field_name, field in self._declared_fields.items():
            # Add missing required data
            if field.required:
                self._generate_missing_required_data(field_name)

            invalid_values: List[Union[InvalidValue, InvalidDictValue]] = field.generate_invalid_values()

            for invalid_value in invalid_values:

                valid_data_copy = self.copy_valid_data
                valid_data_copy[field_name] = invalid_value.value
                whold_field = field_name

                if isinstance(invalid_value, InvalidDictValue):
                    whold_field = f'{field_name}.{invalid_value.sub_field}'

                self.add_invalid_data(
                    InvalidData(
                        data=valid_data_copy,
                        field_name=field_name,
                        invalid_reason=invalid_value.type,
                        whold_field=whold_field
                    )
                )

    def get_relation_constraints(self) -> List[RelationConstraint]:
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'relation_constraints'):
            return []

        return self.Meta.relation_constraints

    @property
    def relation_constraints(self) -> List[RelationConstraint]:
        return self.get_relation_constraints()

    class Meta:

        relation_constraints: List[RelationConstraint] = []
