from typing import Optional, List
from eagle.faker.bases import Faker
from eagle.testcase.check_points import HttpStatusCodeCheckPoint
from eagle.http.client import AuthenticatedHttpClient
from eagle.testcase.unit import HttpUnitTestCase
from eagle.testcase.check_points import CheckPoint
from eagle.http.hooks import log_response


class TestCaseGenerator:

    default_invalid_check_point = HttpStatusCodeCheckPoint(400)
    default_valid_check_point = HttpStatusCodeCheckPoint(200)

    def __init__(
        self,
        method: str,
        url: str,
        faker: Faker,
        client: Optional[AuthenticatedHttpClient] = None,
        valid_check_points: Optional[List[CheckPoint]] = None,
        default_invalid_check_points: Optional[List[CheckPoint]] = None,
    ) -> None:
        self.method = method
        self.url = url
        self.faker = faker
        self.client = client
        self.test_cases = []

        # valid test case check points
        # if not provided, default_valid_check_point will be used
        # example:
        #    {
        #     InvalidProviderType.MISSING_REQUIRED_FIELD: [HttpStatusCodeCheckPoint(400)]
        #    }
        self.invalid_point = {}

        # invalid test case check points
        # if not provided, default_invalid_check_point will be used
        self.valid_check_points = valid_check_points or [self.default_valid_check_point]

        self.default_invalid_check_points = default_invalid_check_points or [self.default_invalid_check_point]

    def get_invalid_check_points(self, invalid_reason: str) -> List[CheckPoint]:
        return self.invalid_point.get(invalid_reason, self.default_invalid_check_points)

    def register_test_case(self, test_case: HttpUnitTestCase):
        self.test_cases.append(test_case)

    def register_valid_check_point(self, check_point: CheckPoint):
        if check_point not in self.valid_check_points:
            self.valid_check_points.append(
                check_point
            )

    def register_invalid_check_point(self, invalid_reason: str, check_point: CheckPoint):
        if invalid_reason not in self.invalid_point:
            self.invalid_point[invalid_reason] = []

        check_points = self.invalid_point[invalid_reason]
        if check_point not in check_points:
            check_points.append(check_point)

    def generate_valid_test_case(self):
        test_case = HttpUnitTestCase(
            method=self.method,
            url=self.url,
            client=self.client,
            json=self.faker.valid_data,
            check_points=self.valid_check_points,
            response_hooks=[log_response],
        )
        self.register_test_case(test_case)

    def generate_invalid_test_case(self):
        for invalid_data in self.faker.invalid_data:
            test_case = HttpUnitTestCase(
                method=self.method,
                url=self.url,
                client=self.client,
                json=invalid_data.data,
                check_points=self.get_invalid_check_points(invalid_data.invalid_reason),
                name=f"< AUTO: {invalid_data.whold_field} | {invalid_data.invalid_reason} >",
                response_hooks=[log_response]
            )
            self.register_test_case(
                test_case
            )

    def generate(self):
        self.generate_valid_test_case()
        self.generate_invalid_test_case()
        return self.test_cases
