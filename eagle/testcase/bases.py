import abc
from colorama import Fore
from eagle.testcase.check_points.bases import CheckPoint


class TestCase:

    _name = None

    def __init__(self, name=None):
        self.name = name or self._name
        self.passed = True
        self.failed_check_points = []

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def do_fail(self, check_point: CheckPoint):
        self.passed = False
        self.failed_check_points.append(check_point)

    def show(self):
        if self.passed:
            print(Fore.GREEN, f"{self.name} PASSED")
        else:
            print(Fore.RED, f"{self.name} FAILURE")
            print(Fore.RED, "=========================================< Reasons >=========================================")
            for i, check_point in enumerate(self.failed_check_points, 1):
                print(Fore.RED, f"Check Point {i}: {check_point.error_message}")
