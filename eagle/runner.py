import os
import sys
from typing import Any, Dict, Optional
from eagle.http.client import AuthenticatedHttpClient
from importlib import import_module
import importlib.util
from eagle.logger import logger
from eagle.usecase.bases import UnitTestCase
from eagle.usecase.suitus import TestSuitus


class Runner:

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Runner':
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'Runner':
        ...

    def __init__(self, root_path: str, client_path: Optional[str] = None) -> None:
        self.root_path = root_path
        self.client = self._get_or_create_client(client_path)
        self.cases = []

    def _get_or_create_client(self, client_path: Optional[str] = None) -> AuthenticatedHttpClient:
        if client_path is None:

            # if client_path is None, we assume that the client is in the root_path
            # and is named client.py
            # if it doesn't exist, we create a new client
            client_path = os.path.join(self.root_path, 'client.py')
            if not os.path.exists(client_path):
                return AuthenticatedHttpClient()

        logger.info(f'Loading client from {client_path}...')
        spec = importlib.util.spec_from_file_location("client", client_path)
        client_module = importlib.util.module_from_spec(spec)
        sys.modules["client"] = client_module
        spec.loader.exec_module(client_module)

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

    def add_case(self, test_case: UnitTestCase) -> None:
        self.cases.append(test_case)

    def load_case_from_yaml(self, yaml_file: str) -> None:
        ...

    def load_case_from_module(self, module_string: str) -> None:
        spec = importlib.util.spec_from_file_location("module_string", module_string)
        module = importlib.util.module_from_spec(spec)
        sys.modules["module_string"] = module
        spec.loader.exec_module(module)

        for var_name in dir(module):
            cls = getattr(module, var_name)
            if cls is UnitTestCase or cls is TestSuitus:
                continue
            if isinstance(cls, type) and issubclass(cls, (UnitTestCase, TestSuitus)):
                logger.info(f'Collecting {cls._name}: {cls.__name__} from {module_string}')
                self.add_case(cls())

    def auto_discover(self) -> None:
        logger.info(f'Auto discovering test cases in {self.root_path}...')
        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f'No such directory: {self.root_path}')

        for root, _, files in os.walk(self.root_path):
            for file_name in files:

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
        self.auto_discover()
        for case in self.cases:
            case.execute()

        for case in self.cases:
            case.show_result()
