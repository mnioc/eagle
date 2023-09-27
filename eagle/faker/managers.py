from typing import List
from eagle.http.client import AuthenticatedHttpClient
from eagle.testcase import APIEndpointTestCase, CheckPoint
from eagle.testcase.check_points.http import HttpStatusCodeEqual


class AutoTestCaseManager:

    default_valid_check_point = HttpStatusCodeEqual(200)
    default_invalid_check_point = HttpStatusCodeEqual(400)

    def _generate_case(
        self,
        method: str,
        url: str,
        name: str,
        client: AuthenticatedHttpClient | None = None,
        check_points: list | None = None,
        **kwargs,
    ) -> APIEndpointTestCase:

        if check_points is None:
            check_points = []

        return APIEndpointTestCase(
            name=name,
            method=method,
            url=url,
            check_points=check_points,
            client=client,
            **kwargs,
        )

    def create(
        self,
        method: str,
        url: str,
        name: str | None = None,
        client: AuthenticatedHttpClient | None = None,
        case_type: str = 'all',
        valid_check_points: List[CheckPoint] | None = None,
        default_invalid_check_points: List[CheckPoint] | None = None,
    ) -> List[APIEndpointTestCase]:
        """
        Create a test case (`APIEndpointTestCase`).

        Args:
            method (str): HTTP method.
            url (str): URL.
            name (str, optional): Test case name. Defaults to None.
            client (AuthenticatedHttpClient, optional): HTTP client. Defaults to None.
            check_points (List[HttpResponseCheckPoint], optional): Check points. Defaults to None.
            case_type (str, optional): Test case type. Defaults to 'valid'.
                available values: ['valid', 'invalid', 'all'].
            valid_check_points (List[CheckPoint], optional): Valid check points. Defaults to None.
            default_invalid_check_points (List[CheckPoint], optional): Default invalid check points. Defaults to None.

        Returns:
            List[APIEndpointTestCase]: Test cases.
        """
        cases = []
        faker = self.faker_cls()

        if case_type in {'valid', 'all'}:
            case = self._generate_case(
                method=method,
                url=url,
                name=name,
                client=client,
                check_points=valid_check_points or [self.default_valid_check_point],
                json=faker.valid_data
            )
            cases.append(case)

        if case_type in {'invalid', 'all'}:
            for invalid_data in faker.invalid_data:
                case = self._generate_case(
                    method=method,
                    url=url,
                    name=name,
                    client=client,
                    check_points=default_invalid_check_points or [self.default_invalid_check_point],
                    json=invalid_data.data
                )
                cases.append(case)

        return cases, faker

    def __get__(self, instance, faker_cls):
        if faker_cls is not None:
            self.faker_cls = faker_cls
        return self


class Manager:

    def __get__(self, instance, faker_cls):
        self.faker_cls = faker_cls
        return self

    def create(
        self,
        url: str,
        client: AuthenticatedHttpClient | None = None,
        **kwargs
    ):
        if client is None:
            client = AuthenticatedHttpClient()

        return client.request(
            method='POST', url=url, json=self.faker_cls().valid_data, **kwargs
        )
