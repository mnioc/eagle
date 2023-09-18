from eagle.http.auth import BearerTokenAuthentication
from eagle.http.client import AuthenticatedHttpClient
from eagle.http.enums import HttpAuthType

# NOTE: This is an example of how to write a client.
# If your interface uses Bearer Token authentication,
# then you can write it like this.
# Of course, if your interface does not have any authentication,
# you don’t even need to write this client.
# The purpose of writing this client is to make your test cases more concise.
# You do not need to write the authentication logic in every test case.
client = AuthenticatedHttpClient.get_client(
    HttpAuthType.BEARER,
    endpoint='http://xx/api',
    authentication=BearerTokenAuthentication(
        token_url="http://xx/api/login",
        auth_body={
            'username': 'admin',
            'password': 'password'
        },
        auth_variables={
            'access_token': '$.tokens.access',
        },
        bearer_auth_headers_template={
            'Authorization': 'Bearer {access_token}',
        }
    )
)
