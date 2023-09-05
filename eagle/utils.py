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


def show_data_table(data: Union[Dict[str, Any], List[Any]]):
    if not data:
        return

    if isinstance(data, dict):
        data = [data]

    if isinstance(data, list):
        max_keys_data = max(data, key=lambda item: len(item.keys()))
        titles = list(max_keys_data.keys())

        table = PrettyTable()
        table.field_names = titles

        for item in data:
            row_data = [to_long_data(item.get(title)) for title in titles]
            table.add_row(row_data)

        print(table)
