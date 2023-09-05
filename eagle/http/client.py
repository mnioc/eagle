import requests
import abc
import inspect
from typing import Any, Type, Dict, Optional
from requests.models import Response, Request
from eagle.enums import HttpAuthType
from eagle.http.auth import Authentication
from eagle.http.hooks import log_response


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

    def __init__(self, endpoint: str = None, authentication: Optional[Authentication] = None, **kwargs: Any):
        super().__init__(endpoint, **kwargs)
        self.authentication = authentication

    @classmethod
    def get_client(cls, auth_type: Optional[str] = None, **kwargs: Any) -> 'AuthenticatedHttpClient':
        """
        This method is used to get the client object.
        """
        if not auth_type:
            return cls(**kwargs)
        if auth_type not in cls.auth_registry:
            raise ValueError(f'Invalid auth type: {auth_type}')
        return cls.auth_registry[auth_type](**kwargs)

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ):
        """Constructs a :class:`Request <Request>`, prepares it and sends it.
        Returns :class:`Response <Response>` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the
            :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the
            :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the
            :class:`Request`.
        :param files: (optional) Dictionary of ``'filename': file-like-objects``
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        :rtype: requests.Response
        """
        # Create the Request.
        if self.endpoint:
            url = self.endpoint + url

        hooks = hooks or {
            'response': [],
        }
        if 'response' not in hooks:
            hooks['response'] = []

        hooks['response'].append(log_response)

        req = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=cookies,
            hooks=hooks,
        )

        if self.authentication:
            req = self.authentication.set_authentication(req)

        prep = self.prepare_request(req)

        proxies = proxies or {}

        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            "timeout": timeout,
            "allow_redirects": allow_redirects,
        }
        send_kwargs |= settings
        return self.send(prep, **send_kwargs)

    def send_request(self, request: Request, **kwargs: Any) -> Response:
        """
        This method is used to send a request.
        """
        if self.endpoint and 'http' not in request.url:
            request.url = self.endpoint + request.url
        if self.authentication:
            request = self.authentication.set_authentication(request)
        request.register_hook('response', log_response)
        prep = self.prepare_request(request)
        return self.send(prep, **kwargs)


class BasicAuthenticatedClient(AuthenticatedHttpClient):
    """
    This class is used to send HTTP requests with basic authentication.
    """
    auth_type = HttpAuthType.BASIC


class BearerAuthenticatedHttpClient(AuthenticatedHttpClient):
    """
    This class is used to send HTTP requests with bearer authentication.
    """
    auth_type = HttpAuthType.BEARER

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        response = super().request(method, url, **kwargs)

        # If the response status code is 401, it means that the token has expired.
        # Then we need to refresh the token and retry the request.
        if response.status_code == 401:
            self.authentication.refresh_token()
            response = super().request(method, url, **kwargs)

        return response

    def send_request(self, request: Request, **kwargs: Any) -> Response:
        response = super().send_request(request, **kwargs)

        # If the response status code is 401, it means that the token has expired.
        # Then we need to refresh the token and retry the request.
        if response.status_code == 401:
            self.authentication.refresh_token()
            response = super().send_request(request, **kwargs)

        return response
