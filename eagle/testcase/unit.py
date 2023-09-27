from typing import (
    Optional,
    Dict,
    Any,
    Callable,
    List
)
from eagle.http.hooks import log_response
from requests.models import Request
from eagle.http.client import AuthenticatedHttpClient
from eagle.testcase.check_points.http import HttpResponseCheckPoint
from eagle.testcase.bases import TestCase


class APIEndpointTestCase(TestCase):
    """
    API single point testing is used to test a specific API endpoint.
    """

    def __init__(
        self,
        method: str,
        url: str,
        name: Optional[str] = None,
        client: Optional[AuthenticatedHttpClient] = None,
        check_points: Optional[List[HttpResponseCheckPoint]] = None,
        response_hooks: List[Dict[str, Any]] | None = None,
        **kwargs,
    ):
        """
        Args:
            method (str): HTTP method.
            url (str): URL.
            name (str, optional): Test case name. Defaults to None.
            client (AuthenticatedHttpClient, optional): HTTP client. Defaults to None.
            check_points (List[HttpResponseCheckPoint], optional): Check points. Defaults to None.
            response_hooks (List[Callable], optional): Response hooks. Defaults to None.
                e.g. [
                    {
                        'args': [],
                        'kwargs': {},
                        'func': log_response
                    }
                ]
            **kwargs: Keyword arguments for requests.models.Request.
        """
        if name is None:
            name = f"{method} {url}"
        super().__init__(name)
        self.client = client
        if self.client is None:
            self.client = AuthenticatedHttpClient()

        self.request = Request(
            method=method.upper(),
            url=url,
            **kwargs,
        )
        self.response = None

        self.check_points = check_points or []
        self.response_hooks = response_hooks
        if self.response_hooks is None:
            self.response_hooks = []

        self.response_hooks.append({
                'args': [],
                'kwargs': {},
                'func': log_response
            })

    def execute_response_hooks(self, response) -> None:
        for hook in self.response_hooks:
            func = hook['func']
            func(response, *hook.get('args', []), **hook.get('kwargs', {}))

    def execute_check_points(self, response) -> None:
        for check_point in self.check_points:
            check_point(response)
            if check_point.failed:
                self.do_fail(check_point)

    def execute(self) -> None:
        self.response = self.client.send_request(self.request)
        self.execute_response_hooks(self.response)
        self.execute_check_points(self.response)
