import re
import string
import random
from typing import Any, Dict, List, Union
from jsonpath_rw import parse
from prettytable import PrettyTable


def to_long_data(data):
    if not data:
        return ' '
    return '...' if len(str(data)) > 50 else data


def get_value_from_json_path(
    json_data: Union[Dict[str, Any], List[Any]],
    json_path_expr: str,
):
    json_path_parser = parse(json_path_expr)
    return match[0].value if (match := json_path_parser.find(json_data)) else None


def show_data_table(data: Union[Dict[str, Any], List[Any]], title: str = '', ignore_keys: List[str] = None):
    if ignore_keys is None:
        ignore_keys = []

    if not data:
        table = PrettyTable()
        table.title = title
        table.field_names = ['No data']
        print(table)
        return

    if isinstance(data, dict):
        data = [data]

    if isinstance(data, list):
        _extracted_from_show_data_table_12(data, ignore_keys, title)


# TODO Rename this here and in `show_data_table`
def _extracted_from_show_data_table_12(data, ignore_keys, title):
    max_keys_data = max(data, key=lambda item: len(item.keys()))
    titles = [key for key in max_keys_data.keys() if key not in ignore_keys]

    table = PrettyTable()
    table.title = title
    table.field_names = titles
    for item in data:
        row_data = [to_long_data(item.get(title)) for title in titles if title not in ignore_keys]
        table.add_row(row_data)
    print(table)


def is_valid_url(url):
    url_pattern = r'^(https?|)://[^\s/$.?#].[^\s]*$'

    if re.match(url_pattern, url):
        return True
    else:
        return False


def generate_random_string(length=10, allow_string=string.ascii_letters+string.digits):
    return ''.join(random.choice(allow_string) for _ in range(length))
