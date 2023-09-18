from typing import (
    Optional,
    Dict,
    Any,
    Callable,
    List
)
from requests.models import Request
from eagle.testcase.bases import TestCase
from eagle.http.client import AuthenticatedHttpClient
from eagle.testcase.check_points import CheckPoint


class HttpUnitTestCase(TestCase):

    def __init__(
        self,
        method: str,
        url: str,
        name: Optional[str] = None,
        client: Optional[AuthenticatedHttpClient] = None,
        headers: Optional[Dict] = None,
        files: Optional[Any] = None,
        data: Optional[Any] = None,
        params: Optional[Any] = None,
        auth: Optional[Any] = None,
        cookies: Optional[Any] = None,
        json: Optional[Dict] = None,
        response_hooks: Optional[List[Callable]] = None,
        check_points: Optional[List[CheckPoint]] = None,
    ):
        super().__init__()
        self.client = client
        self.name = name
        if self.name is None:
            self.name = f"{method} {url}"
        if self.client is None:
            self.client = AuthenticatedHttpClient()

        self.request = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=cookies,
        )
        self.response = None

        self.response_hooks = response_hooks or []
        self.check_points = check_points or []

    def execute_response_hooks(self, response) -> None:
        for hook in self.response_hooks:
            hook(response)

    def execute_check_points(self, response) -> None:
        for check_point in self.check_points:
            check_point(response)
            if not check_point.satisfied:
                self.do_fail(check_point)

    def register_response_hook(self, hook: Callable) -> None:
        self.response_hooks.append(hook)

    def register_check_point(self, check_point: CheckPoint) -> None:
        self.check_points.append(check_point)

    def execute(self, *args, **kwagrs) -> None:
        self.response = self.client.send_request(self.request)
        self.execute_response_hooks(self.response)
        self.execute_check_points(self.response)
