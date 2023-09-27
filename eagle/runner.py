import os
import sys
from typing import Any, Dict, Optional
from eagle.http.client import AuthenticatedHttpClient
from importlib import import_module
import importlib.util
from eagle.logger import logger
from eagle.testcase.unit import APIEndpointTestCase
from eagle.testcase.suitus import APITestSuite, FakerAutoTestSuite
from eagle.testcase.evaluator import TestEvaluator


class Runner:

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Runner':
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'Runner':
        ...

    def __init__(
        self,
        root_path: str,
        client_path: Optional[str] = None,
        prefix: str | None = None,
    ) -> None:
        self.root_path = root_path
        self.client = self._get_or_create_client(client_path)
        self.cases = []
        self.evaluator = None
        self.prefix = prefix

    def _get_or_create_client(self, client_path: Optional[str] = None) -> AuthenticatedHttpClient:
        if client_path is None:

            # if client_path is None, we assume that the client is in the root_path
            # and is named client.py
            # if it doesn't exist, we create a new client
            client_path = os.path.join(self.root_path, 'client.py')
            if not os.path.exists(client_path):
                return AuthenticatedHttpClient()

        logger.info(f'Loading client from {client_path}...')
        spec = importlib.util.spec_from_file_location('client', client_path)
        result = importlib.util.module_from_spec(spec)
        sys.modules['client'] = result
        client_module = spec.loader.exec_module(result)

        # we assume that the client is the first AuthenticatedHttpClient instance
        # in the client module
        # if it doesn't exist, we create a new client.
        try:
            client = next(
                client
                for var_name in dir(client_module)
                if isinstance(client := getattr(client_module, var_name), AuthenticatedHttpClient)
            )
            return client
        except StopIteration:
            logger.warning(f'No AuthenticatedHttpClient instance found in {client_path}')
            logger.warning('Creating a new AuthenticatedHttpClient instance.')
            return AuthenticatedHttpClient()

    def add_case(self, test_case: APIEndpointTestCase) -> None:
        self.cases.append(test_case)

    def extend_cases(self, test_cases: list) -> None:
        self.cases.extend(test_cases)

    def load_case_from_yaml(self, yaml_file: str) -> None:
        ...

    def load_case_from_module(self, module_string: str) -> None:
        spec = importlib.util.spec_from_file_location('dynamic_module', module_string)
        result = importlib.util.module_from_spec(spec)
        sys.modules['dynamic_module'] = result
        spec.loader.exec_module(result)

    def auto_discover(self) -> None:
        logger.info(f'Auto discovering test cases in {self.root_path}...')
        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f'No such directory: {self.root_path}')

        for root, _, files in os.walk(self.root_path):
            for file_name in files:

                if self.prefix is not None and not file_name.startswith(self.prefix):
                    continue

                # we assume that the test case is in the root_path
                # and is named test_*.py or test_*.yaml
                if file_name.startswith("test_"):
                    _, file_ext = os.path.splitext(file_name)

                    # we assume that the test case is a python module
                    # and is named test_*.py
                    if file_ext == ".py":
                        module_path = os.path.join(root, file_name)
                        self.load_case_from_module(module_path)

                    elif file_ext == ".yaml":
                        yaml_path = os.path.join(root, file_name)
                        self.load_case_from_yaml(yaml_path)

    def run(self) -> None:
        from eagle.testcase.registry import registry
        # print(registry.get_test_cases())
        self.auto_discover()
        # print(registry.get_test_cases())
        self.cases = registry.get_test_cases()
        for case in self.cases:
            case.execute()
        self.evaluator = TestEvaluator(self.cases)
        self.evaluator.show_test_result()
