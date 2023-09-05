from eagle.http.auth import BearerTokenAuthentication
from eagle.http.client import AuthenticatedHttpClient
from eagle.enums import HttpAuthType


client = AuthenticatedHttpClient.get_client(
    HttpAuthType.BEARER,
    endpoint='http://10.33.16.93:9999/api/mangrove',
    authentication=BearerTokenAuthentication(
        token_url="http://10.33.16.93:9999/api/auth/login",
        auth_body={
            'email': 'default-admin@mangrove.com',
            'password': 'password'
        },
        auth_variables={
            'access_token': '$.tokens.access',
            'selected_district': '$.selectedDistrict'
        },
        bearer_auth_headers_template={
            'Authorization': 'Bearer {access_token}',
            'District': '{selected_district}'
        }
    )
)
