from typing import Dict, Optional
from requests.models import Request
from eagle.http.client import AuthenticatedHttpClient
from eagle.usecase.assertions import EagleAssertionError
from colorama import Fore


class BaseUseCase:

    def __init__(self):

        # This variable is used to store the result of the use case.
        # It is set to True if the use case passes and False otherwise.
        self.passed = True

        self.not_passed_reason = []

    def do_fail(self, reason: Dict) -> None:
        self.passed = False
        self.not_passed_reason.append(reason)

    def show_result(self) -> None:

        if not hasattr(self, 'name') or self.name is None:
            self.name = self.__class__.__name__

        if self.passed:
            print(Fore.GREEN, f"{self.name} Passed...")
        else:
            print(Fore.RED, f"{self.name} Failed...")
            print(Fore.RED, "=========================================< Reasons >=========================================")
            for reason in self.not_passed_reason:
                print(Fore.RED, reason)

    def execute(self, *args, **kwargs) -> None:
        pass


class UnitTestCase(BaseUseCase):
    """
    This class is used to implement the use case pattern.
    """
    _name = 'Unit Test Case'

    def __init__(self, client: AuthenticatedHttpClient, name: Optional[str] = None):
        super().__init__()
        self.client = client

        self.name = name
        if self.name is None:
            self.name = self.__class__.__name__

        self.request = None
        self.response = None

        # This dictionary is used to store the response hooks.
        # The keys are the events and the values are the hooks.
        # The hooks are called in the order they are registered.
        self.response_hooks = {}

    def build_request(
        self,
        method=None,
        url=None,
        headers=None,
        files=None,
        data=None,
        params=None,
        auth=None,
        cookies=None,
        hooks=None,
        json=None,
    ) -> None:
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
            hooks=hooks
        )

    def register_response_hook(self, event: str, hook: callable, hook_kwargs: Optional[Dict] = None) -> None:
        if hook_kwargs is None:
            hook_kwargs = {}
        self.response_hooks[event] = {
            "hook_func": hook,
            "hook_kwargs": hook_kwargs
        }

    def execute(self, should_raise=False) -> None:
        self.response = self.client.send_request(self.request)
        for event, hook in self.response_hooks.items():
            try:
                hook["hook_func"](self.response, **hook["hook_kwargs"])
            except EagleAssertionError as e:
                self.do_fail({
                    "event": event,
                    "error": e
                })
                if should_raise:
                    raise e
