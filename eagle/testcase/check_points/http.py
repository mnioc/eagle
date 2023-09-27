from requests.models import Response
from eagle.testcase.check_points.bases import CheckPoint
from eagle.utils import get_value_from_json_path
from eagle.http.client import AuthenticatedHttpClient
from datetime import datetime
import pytz


class HttpResponseCheckPoint(CheckPoint):
    ...


class HttpStatusCodeEqual(HttpResponseCheckPoint):

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


class HttpResponseValueCheckPoint(HttpResponseCheckPoint):

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
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        value = get_value_from_json_path(res_data, self.json_path)
        if value != self.expected_value:
            self.do_fail(
                self._error_messages.format(
                    json_path=self.json_path,
                    expected_value=self.expected_value,
                    value=value,
                )
            )


class HttpResponseValueInListItemsCheckPoint(HttpResponseCheckPoint):
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
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        data = get_value_from_json_path(res_data, self.root_json_path)
        if not data:
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


class HttpResponseValueContainCheckPoint(HttpResponseCheckPoint):
    """
    Check if the value of the json path is in the list of items.
    e.g.:
    {
        "results": [
            {
                "id": 1,
                "name": "Timomn"
            },
            {
                "id": 2,
                "type": "Timo"
            }
    }
    If we want to check if the type value of all items in the results list is equal to the expected value
    then we can use this check point.
    usage:
        >>> check_point = HttpResponseValueContainCheckPoint(expected_value='Timo', key='name', root_json_path='$.results')
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
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        data = get_value_from_json_path(res_data, self.root_json_path)
        if not data:
            # self.do_fail(
            #     self._error_messages.format(
            #         json_path=self.root_json_path,
            #         expected_value=self.expected_value,
            #         value_list=[],
            #     )
            # )
            return

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    value = item[self.key]
                    if isinstance(value, str) and self.expected_value not in value:
                        self.do_fail(
                            self._error_messages.format(
                                json_path=self.root_json_path,
                                expected_value=self.expected_value,
                                value_list=[item.get(self.key) for item in data],
                            )
                        )
                    elif isinstance(item, list):
                        for i in value:
                            found = False
                            if self.expected_value in i:
                                found = True
                        if not found:
                            self.do_fail(
                                self._error_messages.format(
                                    json_path=self.root_json_path,
                                    expected_value=self.expected_value,
                                    value_list=[item.get(self.key) for item in data],
                                )
                            )


class HttpResponseJsonIncludeCheckPoint(HttpResponseCheckPoint):

        _error_messages = 'Invalid response json. Expected {expected_key}={expected_value}, but got {key}={value}.'
        _name = 'http_response_json_include'

        def __init__(
            self,
            include_json: dict,
            data_json_path: str,
        ):
            self.include_json = include_json
            self.data_json_path = data_json_path

        def __call__(self, response: Response) -> None:
            try:
                data = response.json()
            except Exception as e:
                self.do_fail(f'Invalid response json, cannot decode json, {e}')
                return
            value = get_value_from_json_path(data, self.data_json_path)
            for expect_key, expect_value in self.include_json.items():
                if expect_key in value and value[expect_key] != expect_value:
                    self.do_fail(
                        self._error_messages.format(
                            expected_key=expect_key,
                            expected_value=expect_value,
                            key=expect_key,
                            value=value[expect_key]
                        )
                    )
                    return


class HttpResponseListPaginationCheckPoint(HttpResponseCheckPoint):

    _name = 'http_response_list_pagination'
    _error_messages = 'Invalid response pagination, expected count: {expected_count}, but got: {got_count}, total: {total}'

    def __init__(
        self,
        data_json_path: str,
        expected_count: int,
        total_key: str,
        data_list_key: str,
    ) -> None:
        self.data_json_path = data_json_path
        self.expected_count = expected_count
        self.total_key = total_key
        self.data_list_key = data_list_key

    def __call__(self, response: Response) -> None:
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        data = get_value_from_json_path(res_data, self.data_json_path)
        total = data.get(self.total_key)
        if int(self.expected_count) != len(data.get(self.data_list_key, [])) and len(data.get(self.data_list_key, [])) > total:
            self.do_fail(
                self._error_messages.format(
                    expected_count=self.expected_count,
                    total=total,
                    got_count=len(data.get(self.data_list_key, []))
                )
            )


class HttpResponseDateCheckPoint(HttpResponseCheckPoint):

    _name = 'http_response_date'
    _error_messages = 'Invalid response date, expected date: {expected_date}, but got: {got_date}'

    def __init__(
        self,
        expected_date: str,
        key: str,
        root_json_path: str,
        compare_type: str = 'eq',
        pattern: str = '%Y-%m-%d %H:%M:%S',
        value_pattern: str = '%Y-%m-%d %H:%M:%S',
        pytz_timezone: str = 'Asia/Shanghai',
    ) -> None:
        self.key = key
        self.root_json_path = root_json_path
        self.compare_type = compare_type
        self.pattern = pattern
        self.pytz_timezone = pytz_timezone
        self.expected_date = datetime.strptime(expected_date, self.pattern).astimezone(pytz.timezone(self.pytz_timezone))
        self.value_pattern = value_pattern
    
    def __call__(self, response: Response) -> None:
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        data = get_value_from_json_path(res_data, self.root_json_path)
        if not data:
            return

        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    value = item.get(self.key)
                    value = datetime.strptime(value, self.value_pattern).astimezone(pytz.timezone(self.pytz_timezone))
                    if (
                        self.compare_type == 'eq'
                        and value != self.expected_date
                        or self.compare_type != 'eq'
                        and self.compare_type == 'gt'
                        and value <= self.expected_date
                        or self.compare_type != 'eq'
                        and self.compare_type != 'gt'
                        and self.compare_type == 'lt'
                        and value >= self.expected_date
                    ):
                        self.do_fail(
                            self._error_messages.format(
                                expected_date=self.expected_date,
                                got_date=value,
                            )
                        )


class HttpResponseDateRangeCheckPoint(HttpResponseCheckPoint):
    _name = 'http_response_date_range'
    _error_messages = 'Invalid response date, expected date: {expected_date}, but got: {got_date}'

    def __init__(
        self,
        expected_date_range: str,
        key: str,
        root_json_path: str,
        pattern: str = '%Y-%m-%d %H:%M:%S',
        value_pattern: str = '%Y-%m-%d %H:%M:%S',
        pytz_timezone: str = 'Asia/Shanghai'
    ):
        self.key = key
        self.root_json_path = root_json_path
        self.pattern = pattern
        self.pytz_timezone = pytz_timezone
        self.value_pattern = value_pattern
        self.expected_date_range = [datetime.strptime(date, self.pattern).astimezone(pytz.timezone(self.pytz_timezone)) for date in expected_date_range]

    def __call__(self, response: Response) -> None:
        try:
            res_data = response.json()
        except Exception as e:
            self.do_fail(f'Invalid response json, cannot decode json, {e}')
            return
        data = get_value_from_json_path(res_data, self.root_json_path)
        if not data:
            return

        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    value = item.get(self.key)
                    value = datetime.strptime(value, self.value_pattern).astimezone(pytz.timezone(self.pytz_timezone))
                    if not self.expected_date_range[0] <= value <= self.expected_date_range[1]:
                        self.do_fail(
                            self._error_messages.format(
                                expected_date=self.expected_date_range,
                                got_date=value,
                            )
                        )
        


class CallAPICheckPoint(CheckPoint):

    def __init__(
        self,
        method: str,
        url: str,
        client: AuthenticatedHttpClient | None = None,
        check_points: list[HttpResponseCheckPoint] | None = None,
        **kwargs
    ) -> None:
        self.method = method
        self.url = url
        self.client = client
        if self.client is None:
            self.client = AuthenticatedHttpClient()
        self.check_points = check_points
        if self.check_points is None:
            self.check_points = []
        self.response = None
        self.request_kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.response = self.client.request(self.method, self.url, **self.request_kwargs)
        for check_point in self.check_points:
            check_point(self.response)

        for point in self.check_points:
            if point.failed:
                self.do_fail(point.error_message)
                break

        return self.response
