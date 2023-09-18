import inspect
from typing import List, Optional
from eagle.testcase.unit import HttpUnitTestCase
from colorama import Fore
from prettytable import PrettyTable
import json
from eagle.testcase.generator import TestCaseGenerator


class AutoMixin:

    def __init__(self, *args, **kwargs):
        self._auto_register()

    def get_generator(self):
        if hasattr(self, 'generator') and self.generator is not None:
            assert isinstance(self.generator, TestCaseGenerator), '`generator` must be `TestCaseGenerator`'
            return self.generator

    def _auto_register(self):
        if generator := self.get_generator():
            for test_case in generator.generate():
                self.register(test_case)


class HttpTestSuite(AutoMixin):

    generator = None
    show_result = True

    def __init__(self, cases: Optional[List[HttpUnitTestCase]] = None):
        self.cases = cases
        if self.cases is None:
            self.cases = []
        super().__init__()

    def register(self, case: HttpUnitTestCase) -> None:
        self.cases.append(case)

    def show(self):
        table = PrettyTable()
        table.field_names = ["case_name", "status", "reason", "body"]

        for case in self.cases:
            body = json.dumps(case.request.json)
            if case.passed:
                print(Fore.GREEN+'-' * 150)
                print(f'case_name | {Fore.GREEN}{case.name}')
                print(f'status    | {Fore.GREEN}PASSED')
                if case.request.json:
                    print(f'body      | {Fore.GREEN}{body}')
            else:
                print(Fore.RED+'-' * 150)
                print(f'case_name | {Fore.RED}{case.name}')
                print(f'status    | {Fore.RED}FAILURE')
                if case.request.json:
                    print(f'body      | {Fore.RED}{body}')
                reason = ''.join(f'<{point.error_message}>' for point in case.not_passed_check_points)
                print(f'reason    | {Fore.RED}{reason}')

    def execute(self) -> None:
        for test_case in self.cases:
            test_case.execute()

        if self.show_result:
            self.show()
