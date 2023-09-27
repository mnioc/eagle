import inspect
from typing import List, Optional
from eagle.testcase.unit import APIEndpointTestCase
from colorama import Fore
from prettytable import PrettyTable
import json
from eagle.testcase.bases import TestCase
from eagle.testcase.check_points.http import HttpStatusCodeEqual


class APITestSuite(TestCase):

    show_result = False
    show_response_body = False

    def __init__(self, cases: Optional[List[APIEndpointTestCase]] = None):
        self._cases = cases
        if self._cases is None:
            self._cases = []
        super().__init__()

    def add_case(self, case: APIEndpointTestCase) -> None:
        assert isinstance(case, APIEndpointTestCase), '`case` must be `APIEndpointTestCase`'
        self._cases.append(case)

    def add_cases(self, cases: List[APIEndpointTestCase]) -> None:
        for case in cases:
            self.add_case(case)

    def show(self):
        table = PrettyTable()
        table.field_names = ["case_name", "status", "reason", "body"]

        for case in self._cases:
            body = json.dumps(case.request.json)
            if case.passed:
                print(Fore.GREEN+'-' * 150)
                print(f'case_name | {Fore.GREEN}{case.name}')
                print(f'status    | {Fore.GREEN}PASSED')
                if case.request.json:
                    print(f'body      | {Fore.GREEN}{body}')
                if self.show_response_body:
                    try:
                        print(f'response  | {Fore.GREEN}{case.response.json()}')
                    except Exception:
                        print(f'response  | {Fore.GREEN}{case.response.text}')
            else:
                print(Fore.RED+'-' * 150)
                print(f'case_name | {Fore.RED}{case.name}')
                print(f'status    | {Fore.RED}FAILURE')
                if case.request.json:
                    print(f'body      | {Fore.RED}{body}')
                reason = ''.join(f'<{point.error_message}>' for point in case.failed_check_points)
                print(f'reason    | {Fore.RED}{reason}')
                if self.show_response_body:
                    try:
                        print(f'response  | {Fore.RED}{case.response.json()}')
                    except Exception:
                        print(f'response  | {Fore.RED}{case.response.text}')

    def execute(self) -> None:
        for test_case in self._cases:
            test_case.execute()

        if self.show_result:
            self.show()


class FakerAutoTestSuite(APITestSuite):
    """
    This class is used to automatically generate test cases.

    Example:

        >>> class UserTestCase(FakerAutoTestSuite):
                caseset = UserFaker.cases.create(method='POST', url='/containers/')
    """

    caseset = []

    def __init__(self):
        caseset = self.get_caseset()
        if not isinstance(caseset, list):
            caseset = [caseset]
        super().__init__(caseset)

    def get_caseset(self):
        return self.caseset
