import inspect
from requests.models import Response
from eagle.utils import get_value_from_json_path
from eagle.logger import logger


class CheckPointLogMetaclass(type):

    def __new__(cls, name, bases, class_attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, class_attrs, **kwargs)
        if not inspect.isabstract(new_cls):
            original_call = new_cls.__call__

            def new_call(self, *args, **kwargs):
                result = original_call(self, *args, **kwargs)
                if self.satisfied:
                    logger.info(f'check: {self._name} | SUCCESS')
                else:
                    logger.error(f'check: {self._name} | FAILURE | {self.error_message}')
                return result
            new_cls.__call__ = new_call
        return new_cls


class CheckPoint(metaclass=CheckPointLogMetaclass):

    _name = ''
    satisfied = True
    error_message = ''

    def __call__(self, *args, **kwargs):
        pass

    def do_fail(self, error_message: str = None):
        self.satisfied = False
        self.error_message = error_message or self.error_message


class HttpStatusCodeCheckPoint(CheckPoint):

    _error_message = 'Invalid status code. Expected {expected_status_code}, but got {code}.'
    _name = 'http_status_code'

    def __init__(self, expected_status_code: int):
        self.expected_status_code = expected_status_code

    def __call__(self, response: Response) -> None:
        if int(response.status_code) != int(self.expected_status_code):
            self.do_fail(
                self._error_message.format(
                    expected_status_code=self.expected_status_code,
                    code=response.status_code,
                )
            )


class HttpResponseJsonCheckPoint(CheckPoint):

    _error_messages = 'Invalid response json. Expected {expected_json}, but got {json}.'
    _name = 'http_response_json'

    def __init__(self, expected_json: dict):
        self.expected_json = expected_json

    def __call__(self, response: Response) -> None:
        if response.json() != self.expected_json:
            self.do_fail(
                self._error_messages.format(
                    expected_json=self.expected_json,
                    json=response.json()
                )
            )


class HttpResponseValueCheckPoint(CheckPoint):

    _error_messages = 'Invalid response value: {json_path}. Expected {expected_value}, but got {value}.'
    _name = 'http_response_value'

    def __init__(
        self,
        expected_value: str,
        json_path: str,
    ):
        self.expected_value = expected_value
        self.json_path = json_path

    def __call__(self, response: Response) -> None:
        value = get_value_from_json_path(response.json(), self.json_path)
        if value != self.expected_value:
            self.do_fail(
                self._error_messages.format(
                    json_path=self.json_path,
                    expected_value=self.expected_value,
                    value=value,
                )
            )


class HttpResponseValueInListItemsCheckPoint(CheckPoint):
    """
    Check if the value of the json path is in the list of items.
    e.g.:
    {
        "results": [
            {
                "id": 1,
                "type": "A"
            },
            {
                "id": 2,
                "type": "A"
            }
    }
    If we want to check if the type value of all items in the results list is equal to the expected value
    then we can use this check point.
    usage:
        >>> check_point = HttpResponseValueInListItemsCheckPoint(expected_value='A', key='type', root_json_path='$.results')
        >>> check_point(response)
        >>> check_point.satisfied
        True
    """

    _error_messages = 'Invalid response value: {json_path}. Expected {expected_value}, but got {value_list}.'
    _name = 'http_response_value_in_list_items'

    def __init__(
        self,
        expected_value: str,
        key: str,
        root_json_path: str,
    ):
        self.expected_value = expected_value
        self.key = key
        self.root_json_path = root_json_path

    def __call__(self, response: Response) -> None:
        data = get_value_from_json_path(response.json(), self.root_json_path)
        if not data:
            self.do_fail(
                self._error_messages.format(
                    json_path=self.root_json_path,
                    expected_value=self.expected_value,
                    value_list=[],
                )
            )
            return

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item[self.key] != self.expected_value:
                    self.do_fail(
                        self._error_messages.format(
                            json_path=self.root_json_path,
                            expected_value=self.expected_value,
                            value_list=[item.get(self.key) for item in data],
                        )
                    )


class UnitTeseCaseCheckPoint(CheckPoint):

    _error_message = 'Unit test case failed.'
    _name = 'unit_test_case'

    def __init__(self, unit_test_case):
        self.unit_test_case = unit_test_case

    def __call__(self, *args, **kwargs) -> None:
        self.unit_test_case.execute()
        if not self.unit_test_case.passed:
            self.do_fail(self.unit_test_case.error_message)
