import requests
import abc
import inspect
from typing import Any, Type, Dict
from requests.models import Response


class HttpClient(requests.Session):
    """
    This class is used to send HTTP requests.
    """
    _instance_ = {}

    # This method is used to implement the singleton pattern.
    # For the same `endpoint` it ensures that only one instance of the class is created.
    # The instance is stored in the class variable _instance_.
    def __new__(cls, endpoint: str = None, **kwargs: Any):
        if not endpoint:
            return super().__new__(cls)
        if endpoint not in cls._instance_:
            cls._instance_[endpoint] = super().__new__(cls)
        return cls._instance_[endpoint]

    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint
        super().__init__()

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        if self.endpoint:
            url = self.endpoint + url
        return super().request(method, url, **kwargs)


class StrategyMeta(abc.ABCMeta):

    auth_registry: Dict[str, Type['AuthenticatedHttpClient']] = {}

    def __new__(cls, name, bases, class_attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, class_attrs, **kwargs)
        if not inspect.isabstract(new_cls):
            cls.auth_registry[new_cls.auth_type] = new_cls
        return new_cls


class AuthenticatedHttpClient(HttpClient, metaclass=StrategyMeta):
    """
    This class is used to send authenticated HTTP requests.
    """
    auth_type: str = None

    def __init__(self, endpoint: str = None, **kwargs: Any):
        super().__init__(endpoint, **kwargs)
        self.auth = self.get_auth(**kwargs)

    @abc.abstractmethod
    def get_auth(self, **kwargs: Any) -> Any:
        """
        This method is used to get the authentication object.
        """
        pass

    @classmethod
    def get_client(cls, auth_type: str, **kwargs: Any) -> 'AuthenticatedHttpClient':
        """
        This method is used to get the client object.
        """
        if auth_type not in cls.auth_registry:
            raise ValueError(f'Invalid auth type: {auth_type}')
        return cls.auth_registry[auth_type](**kwargs)
