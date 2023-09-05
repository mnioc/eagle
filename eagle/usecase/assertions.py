from eagle.logger import logger
from eagle.utils import get_value_from_json_path


class EagleAssertionError(Exception):

    def __init__(self, message: str):
        self.message = message
        logger.error(message)


class ResponseAssertionHook:

    def __call__(self, response):
        return self.response


class AssertStatusCodeEqual(ResponseAssertionHook):

    def __init__(self, expected_status_code: int):
        self.expected_status_code = expected_status_code

    def __call__(self, response):
        if response.status_code != self.expected_status_code:
            raise EagleAssertionError(f"Expected status code {self.expected_status_code}, but got {response.status_code}")
        return response


class AssertResponseDataEqual(ResponseAssertionHook):

    def __init__(self, expected_json: dict):
        self.expected_json = expected_json

    def __call__(self, response):
        if response.json() != self.expected_json:
            raise EagleAssertionError(f"Expected json {self.expected_json}, but got {response.json()}")
        return response


class AssertAllValueEqual(ResponseAssertionHook):

    def __init__(
        self,
        expected_value: str,
        key: str,
        root_json_path: str,
    ):

        # The expected value is the value we expect to get from the response.
        self.expected_value = expected_value

        # To get the value from the response, we need to know the key.
        # For example, if the response is:
        # {
        #     "data": {
        #         "id": 1,
        #         "name": "Eagle"
        #     }
        # }
        # Then the key is "name".
        self.key = key

        # The data path is the path to the data.
        # For example, if the response is:
        # {
        #     "data": {
        #         "id": 1,
        #         "name": "Eagle"
        #     }
        # }
        # Then the data path is "$.data".
        # It is a json path.
        self.root_json_path = root_json_path

    def __call__(self, response):
        data = get_value_from_json_path(response.json(), self.root_json_path)
        if not data:
            raise EagleAssertionError(f"Failed to get data from response. The response is {response.json()}")

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item[self.key] != self.expected_value:
                    raise EagleAssertionError(f"Expected value {self.expected_value}, but got {item[self.key]}")

        return response
