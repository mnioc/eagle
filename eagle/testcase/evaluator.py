from typing import List, Union
from eagle.testcase.unit import HttpUnitTestCase
from eagle.testcase.suitus import HttpTestSuite
from prettytable import PrettyTable
from colorama import Fore
import json


class TestEvaluator:

    def __init__(self, cases: List[Union[HttpUnitTestCase, HttpTestSuite]]):
        self.faliure_cases = []
        self.cases = self._collect_unit_case(cases)

    def _collect_unit_case(self, cases):
        new_cases = []
        for case in cases:
            if isinstance(case, HttpUnitTestCase):
                new_cases.append(case)
                if not case.passed:
                    self.faliure_cases.append(case)
            if isinstance(case, HttpTestSuite):
                new_cases.extend(case.cases)
                for _case in case.cases:
                    if not _case.passed:
                        self.faliure_cases.append(_case)
        return new_cases

    def get_not_passed_cases(self):
        return [
            case for case in self.cases
            if not case.passed
        ]

    @property
    def pass_rate(self):
        return 1 - len(self.faliure_cases) / len(self.cases)

    @property
    def humen_pass_rate(self):
        return f"{self.pass_rate * 100}%"

    def show_test_result(self):
        print(f'{Fore.RESET}')
        print('='*150)
        print("#" + 'TEST RESULT'.center(148) + "#")
        print('='*150)

        if self.faliure_cases:
            print(f'{Fore.RED}')
            for case in self.faliure_cases:
                body = json.dumps(case.request.json)
                response = json.dumps(case.response.json())
                print(f'case_name | {Fore.RED}{case.name}')
                print(f'status    | {Fore.RED}FAILURE')
                print(f'body      | {Fore.RED}{body}')
                reason = ''.join(f'<{point.error_message}>' for point in case.not_passed_check_points)
                print(f'reason    | {Fore.RED}{reason}')
                print(f'response  | {Fore.RED}{response}')
                print(Fore.RED+'-' * 150)

        table = PrettyTable()
        print(Fore.BLUE)
        table.field_names = [f'{Fore.BLUE}total_cases', 'pass', 'faliure', 'pass_rate']
        total = len(self.cases)
        faliure = len(self.faliure_cases)
        table.add_row([f'{Fore.BLUE}{total}', total-faliure, faliure, self.humen_pass_rate])
        print(table)
        print(f'{Fore.RESET}')
