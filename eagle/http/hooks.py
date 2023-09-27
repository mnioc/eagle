from requests.models import Response
from eagle.logger import logger
from eagle.utils import get_value_from_json_path, show_data_table


def log_response(response: Response, *args, **kwargs) -> None:
    """
    This function is used to log the response.
    """
    msg = f'HTTP {response.request.method} {response.request.url} {response.status_code} {response.elapsed.total_seconds()}s'
    if response.status_code >= 500:
        logger.error(msg)
        logger.exception(response.text)
    else:
        logger.info(msg)


def show_response_table(response: Response, response_data_json_path: str, ignore_keys=None, *args, **kwaargs) -> None:
    """
    This function is used to show the response in a table format.
    """
    try:
        data = response.json()
    except Exception:
        return
    data = get_value_from_json_path(data, response_data_json_path)
    show_data_table(data, f'{response.request.method} {response.request.url}', ignore_keys)
