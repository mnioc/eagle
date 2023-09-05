from typing import Dict
from eagle.usecase.bases import BaseUseCase, UnitTestCase
from eagle.usecase.assertions import EagleAssertionError
from eagle.usecase.mocker import AutoGenerateTestCaseMetaclass


class TestSuitus(BaseUseCase, metaclass=AutoGenerateTestCaseMetaclass):

    # List of test functions to skip
    _skip_test_func = []

    _name = 'Test Suitus'

    @classmethod
    def get_client(cls):
        return cls.Meta.client

    def __init__(self):
        super().__init__()

    def execute(self):
        for var_name in dir(self):
            if var_name.startswith("test_") and var_name not in self._skip_test_func:
                test_func = getattr(self, var_name)
                if callable(test_func):
                    try:
                        test_func()
                    except EagleAssertionError as e:
                        self.do_fail({
                            "error": e.message,
                            "event": test_func.__name__
                        })

    class Meta:
        client = None
