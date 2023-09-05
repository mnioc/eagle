from requests.models import Request
import contextlib
import requests
import json
from typing import Optional, Dict
from jsonpath_rw import parse
from eagle.settings.bases import app_settings
from eagle.exceptions import APIAuthFailedException
from eagle.logger import logger
from eagle.enums import HttpAuthType
from eagle.http.hooks import log_response


class Authentication:

    auth_type = None

    def __init__(self, **kwargs):
        pass

    def set_authentication(self, request: Request) -> Request:
        return request


class BasicAuthentication(Authentication):

    auth_type = HttpAuthType.BASIC

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def set_authentication(self, request: Request) -> Request:
        request.auth = (self.username, self.password)
        return request


class BearerTokenAuthentication(Authentication):

    auth_type = HttpAuthType.BEARER

    def __init__(
        self,
        token_url: str,
        auth_body: Dict[str, str],
        auth_variables: Optional[Dict[str, str]],
        bearer_auth_headers_template: Optional[Dict[str, str]],
        token_file: Optional[str] = None,
        retry: Optional[int] = None,
    ):
        """
        Args:
            token_url: The URL of the token endpoint.
            auth_body: The body used to get the token.
            extracted_auth_variables: The variables used to get the token.
                e.g.
                    {
                        "access_token": "$.tokens.access",  # Defines the jsonpath to get access_token value.
                        "refresh_token": "$.tokens.refresh"  # Defines the jsonpath to get refresh_token value.
                    }
            bearer_auth_headers_template: bearer auth headers
                e.g.
                    {
                        "Authorization": "Bearer {access_token}" # Defines the bearer auth headers.
                    }
                access_token is the key in auth_variables.
                It will be replaced by the real access_token value.

            token_file: The file used to cache the token.
        """
        self.token_url = token_url
        self.token_file = token_file
        if self.token_file is None:
            self.token_file = app_settings.TOKEN_CACHE_FILE

        self.auth_body = auth_body

        self.auth_variables = auth_variables

        # The bearer auth headers template.
        # It contains a fillable template
        # which will be replaced by the real access_token value.
        # var name is the key in auth_variables.
        self.bearer_auth_headers_template = bearer_auth_headers_template

        self.retry = retry
        if self.retry is None:
            self.retry = app_settings.TOKEN_RETRY

        # The authentication data.
        # It contains the real access_token value.
        # e.g.
        #   {
        #       "Authorization": "Bearer xxxxxxx" # Defines the bearer auth headers.
        #   }
        self._authentication = {}

        self.get_auth_headers()

    def set_authentication(self, request: Request) -> Request:
        request.headers.update(self.get_auth_headers())
        return request

    def get_auth_headers(self) -> Dict[str, str]:
        if not self._authentication:
            self._authentication = self.fetch_token()
        return self._authentication

    def refresh_token(self):
        self._authentication = {}
        logger.info('Refreshing token...')
        with contextlib.suppress(FileNotFoundError):
            with open(self.token_file, 'w') as f:
                json.dump({}, f)
        return self.get_auth_headers()

    def fetch_token(self) -> Dict[str, str]:
        with contextlib.suppress(FileNotFoundError):
            with open(self.token_file, 'r') as f:
                if auth_data := json.load(f):
                    return auth_data

        # Make a request to the token endpoint to get the new token
        retries = 0
        error_msg = None
        while retries < self.retry:
            try:
                response = requests.post(self.token_url, json=self.auth_body, hooks={'response': log_response})
                response.raise_for_status()
                error_msg = None
                break
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
                retries += 1
                print(response.text)
                error_msg = f"Failed to get the token. {e}"
                logger.warn(f"{error_msg}. Retrying...")

        if error_msg:
            raise APIAuthFailedException(error_msg)

        res_data = response.json()

        # TODO Welcome to explore a more elegant way to achieve !!!
        for key, value in self.auth_variables.items():
            json_path_expr = parse(value)
            if match := json_path_expr.find(res_data):
                auth_val = match[0].value

            for header_key, header_format_string in self.bearer_auth_headers_template.items():
                # Replace the format string with the real value.
                format_key = f'{{{key}}}'
                if format_key in header_format_string:
                    self._authentication[header_key] = header_format_string.replace(format_key, auth_val)

        if self._authentication:
            logger.info("get the token ok.")
            with open(self.token_file, 'w') as f:
                json.dump(self._authentication, f)
                logger.info(f"save the token to {self.token_file}")
            return self._authentication
        else:
            raise APIAuthFailedException("Failed to get the token. The token is empty.")
