from typing import Any
import abc
from colorama import Fore
from eagle.testcase.check_points import CheckPoint, HttpResponseJsonCheckPoint


class TestCase:

    def __init__(self):
        self.passed = True
        self.not_passed_check_points = []

    @abc.abstractmethod
    def execute(self, *args, **kwagrs) -> None:
        pass

    def do_fail(self, check_point: CheckPoint):
        self.passed = False
        self.not_passed_check_points.append(check_point)

    def show(self):
        if self.passed:
            print(Fore.GREEN, f"{self.name} PASSED")
        else:
            print(Fore.RED, f"{self.name} FAILURE")
            print(Fore.RED, "=========================================< Reasons >=========================================")
            for check_point in self.not_passed_check_points:
                print(Fore.RED, check_point.error_message)


class TestCaseRegistry:

    def __init__(self):
        self._test_cases = []

    def register(self, test_case: TestCase):
        self._test_cases.append(test_case)

    def get_test_cases(self):
        return self._test_cases


class TestCaseManager:

    def create(
        self,
        url: str,
        client=None,
        valid_check_points=None,
        default_invalid_check_points=None,
    ):
        setattr(self.faker_class, 'post_url', url)
        from eagle.testcase.generator import TestCaseGenerator
        from eagle.testcase.suitus import HttpTestSuite
        generator = TestCaseGenerator(
            method='POST',
            url=url,
            faker=self.faker_class(),
            client=client,
            valid_check_points=valid_check_points,
            default_invalid_check_points=default_invalid_check_points
        )
        return HttpTestSuite(
            cases=generator.generate()
        )

    def delete(
        self,
        url: str,
        post_url: str,
        context_key: str,
        json_path: str,
        client=None,
        check_points=None,
    ):
        from eagle.testcase.pipeline import HttpTestPipeline, UnitTestCaseSetContextMiddleware, ReplaceUrlFromContextMiddleware

        from eagle.testcase.unit import HttpUnitTestCase
        pipeline = HttpTestPipeline(
            cases=[
                HttpUnitTestCase(
                    method='DELETE',
                    client=client,
                    url=url,
                    check_points=check_points,
                )
            ]
        )

        pipeline.add_pre_execute(
            UnitTestCaseSetContextMiddleware(
                unit_test_case=HttpUnitTestCase(
                    method='POST',
                    client=client,
                    url=post_url,
                    json=self.faker_class().valid_data,
                ),
                context_key=context_key,
                json_path=json_path
            )
        )
        pipeline.add_pre_execute(
            ReplaceUrlFromContextMiddleware(
                context_key=context_key
            )
        )
        return pipeline

    def update(
        self,
        url: str,
        post_url: str,
        context_key: str,
        json_path: str,
        client=None,
        valid_check_points=None,
        default_invalid_check_points=None
    ):
        from eagle.testcase.pipeline import HttpTestPipeline, UnitTestCaseSetContextMiddleware, ReplaceUrlFromContextMiddleware

        from eagle.testcase.unit import HttpUnitTestCase
        from eagle.testcase.generator import TestCaseGenerator

        faker = self.faker_class()

        generator = TestCaseGenerator(
            method='PUT',
            url=url,
            faker=faker,
            client=client,
            valid_check_points=valid_check_points,
            default_invalid_check_points=default_invalid_check_points
        )
        pipeline = HttpTestPipeline(
            cases=generator.generate()
        )

        pipeline.add_pre_execute(
            UnitTestCaseSetContextMiddleware(
                unit_test_case=HttpUnitTestCase(
                    method='POST',
                    client=client,
                    url=post_url,
                    json=faker.valid_data,
                ),
                context_key=context_key,
                json_path=json_path
            )
        )
        pipeline.add_pre_execute(
            ReplaceUrlFromContextMiddleware(
                context_key=context_key
            )
        )
        return pipeline

    def __get__(self, instance: Any, faker_class: Any) -> Any:
        self.faker_class = faker_class
        return self
