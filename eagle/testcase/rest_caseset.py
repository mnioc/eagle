from typing import List
from eagle.testcase.check_points.http import (
    HttpStatusCodeEqual,
    CallAPICheckPoint,
    HttpResponseValueCheckPoint,
    HttpResponseJsonIncludeCheckPoint,
    HttpResponseValueInListItemsCheckPoint,
    HttpResponseValueContainCheckPoint,
    CheckPoint,
    HttpResponseListPaginationCheckPoint
)
import re
from eagle.testcase.unit import APIEndpointTestCase
import inspect
from eagle.faker.bases import Faker
from eagle.http.client import AuthenticatedHttpClient
from eagle.http.hooks import show_response_table
from eagle.logger import logger


class FakerAsTestCaseMixin:

    def generate_valid_case(self, faker: Faker, **kwargs):
        return [APIEndpointTestCase(json=faker.valid_data, **kwargs)]

    def generate_invalid_case(self, faker: Faker, **kwargs):
        return [
            APIEndpointTestCase(json=invalid_data.data, **kwargs)
            for invalid_data in faker.invalid_data
        ]


class CreateApiMixin:
    """
    Create API tese case mixin.
    """

    create_url = None
    create_method = 'POST'
    create_valid_check_points = [HttpStatusCodeEqual(201)]
    create_invalid_check_points = [HttpStatusCodeEqual(400)]
    create_json_path = '$'
    disable_payload_check = False

    def get_create_url(self):
        if self.create_url is None and self.url is None:
            raise AttributeError('`create_url` or `url` is not defined.')
        return self.create_url or self.url

    def get_extra_create_valid_check_points(self, faker):
        if self.disable_payload_check:
            return []
        return [
           HttpResponseJsonIncludeCheckPoint(faker.valid_data, self.create_json_path)
        ]

    def get_create_test_cases(self):
        url = self.get_create_url()
        faker = self.get_faker_class()()
        valid_cases = self.generate_valid_case(
            faker=faker,
            method=self.create_method,
            url=url,
            client=self.client,
            check_points=self.create_valid_check_points + self.get_extra_create_valid_check_points(faker)
        )
        invalid_cases = self.generate_invalid_case(
            faker=faker,
            method=self.create_method,
            url=url,
            client=self.client,
            check_points=self.create_invalid_check_points,
        )

        return valid_cases + invalid_cases


class UpdateApiMixin:
    update_url = None
    update_method = 'PUT'
    update_valid_check_points = [HttpStatusCodeEqual(200)]
    update_invalid_check_points = [HttpStatusCodeEqual(400)]
    update_json_path = '$'
    retrieve_json_path = '$'

    def get_update_url(self):
        if self.update_url is None and self.retrieve_url is None:
            raise AttributeError('`update_url` or `retrieve_url` is not defined.')
        url = self.update_url or self.retrieve_url
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, url)
        variables = list(matches)
        for variable in variables:
            if get_variable_func := getattr(self, f'get_update_{variable}', None):
                url = url.format(**{variable: get_variable_func()})
            else:
                raise AttributeError(f'`get_update_{variable}` is not defined.')
        return url

    def create_retrieve_object(self):
        if getattr(self, 'create_url', None) is None and self.url is None:
            raise AttributeError('`create_url` or `url` is not defined.')
        self.retrieve_object = self.get_faker_class().objects.create(
            url=getattr(self, 'create_url', None) or self.url,
            client=self.client,
        )

    def get_update_pk(self):
        if not getattr(self, 'retrieve_object', None):
            self.create_retrieve_object()
        return self.retrieve_object.json()[self.pk_variable]

    def get_extra_update_valid_check_points(self, faker):
        return [
            HttpResponseJsonIncludeCheckPoint(faker.valid_data, self.update_json_path),
            CallAPICheckPoint(
                method='GET',
                url=self.get_update_url(),
                client=self.client,
                check_points=[
                    HttpStatusCodeEqual(200),
                    HttpResponseValueCheckPoint(self.get_update_pk(), f'{self.retrieve_json_path}.{self.pk_variable}'),
                    HttpResponseJsonIncludeCheckPoint(faker.valid_data, self.retrieve_json_path)
                ]
            )
        ]

    def get_update_test_cases(self, *args, **kwargs):
        url = self.get_update_url()
        faker = self.get_faker_class()()
        valid_cases = self.generate_valid_case(
            faker=faker,
            method=self.update_method,
            url=url,
            client=self.client,
            check_points=self.update_valid_check_points + self.get_extra_update_valid_check_points(faker)
        )
        invalid_cases = self.generate_invalid_case(
            faker=faker,
            method=self.update_method,
            url=url,
            client=self.client,
            check_points=self.update_invalid_check_points,
        )

        return valid_cases + invalid_cases

    def clenup_update_test_cases(self):
        if getattr(self, 'retrieve_object', None):
            url = self.get_update_url()
            self.client.delete(url)

class DeleteApiMixin:

    delete_url = None
    delete_method = 'DELETE'
    delete_check_points = [HttpStatusCodeEqual(204)]

    def get_delete_url(self):
        if self.delete_url is None and self.retrieve_url is None:
            raise AttributeError('`delete_url` or `retrieve_url` is not defined.')
        url = self.delete_url or self.retrieve_url
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, url)
        variables = list(matches)
        for variable in variables:
            if get_variable_func := getattr(self, f'get_delete_{variable}', None):
                url = url.format(**{variable: get_variable_func()})
            else:
                raise AttributeError(f'`get_{variable}` is not defined.')
        return url

    def create_delete_object(self):
        if getattr(self, 'create_url', None) is None and self.url is None:
            raise AttributeError('`create_url` or `url` is not defined.')
        self.delete_object = self.get_faker_class().objects.create(
            url=getattr(self, 'create_url', None) or self.url,
            client=self.client,
        )

    def get_delete_pk(self):
        if not getattr(self, 'delete_object', None):
            self.create_delete_object()
        print(self.delete_object.json())
        return self.delete_object.json()[self.pk_variable]

    def get_extra_delete_check_points(self):
        return [
            CallAPICheckPoint(
                method='GET',
                url=self.get_delete_url(),
                client=self.client,
                check_points=[
                    HttpStatusCodeEqual(404),
                ]
            )
        ]

    def get_delete_test_cases(self, *args, **kwargs):
        url = self.get_delete_url()
        return [
            APIEndpointTestCase(
                method=self.delete_method,
                url=url,
                client=self.client,
                check_points=self.delete_check_points + self.get_extra_delete_check_points()
            )
        ]


class ListApiMixin:
    list_method = 'GET'
    list_check_points = [HttpStatusCodeEqual(200)]
    list_root_json_path = '$'
    list_filters = {}
    list_search = {}
    show_list_response = False
    show_ignore_keys = []
    list_page_size_query_param = None

    def get_extra_list_test_cases(self):
        return []

    def get_response_hooks(self):
        if self.show_list_response:
            return [
                    {
                        'args': [self.list_root_json_path, self.show_ignore_keys],
                        'kwargs': {},
                        'func': show_response_table
                    }
                ]
        return []

    def get_paginated_list_test_cases(self):
        if not self.list_page_size_query_param:
            return []
        cases = []
        for page_size in self.list_page_size_query_param:
            url = f'{self.url}?page_size={page_size}'
            cases.append(
                APIEndpointTestCase(
                    method=self.list_method,
                    url=url,
                    client=self.client,
                    check_points=self.list_check_points + [
                        HttpResponseListPaginationCheckPoint(
                            '$',
                            page_size,
                            'count',
                            'results',
                        )
                    ],
                    response_hooks=self.get_response_hooks()
                )
            )
        return cases
    
    def get_searched_list_test_cases(self):
        if not self.list_search:
            return []
        cases = []
        for search_key, search_value in self.list_search.items():
            url = f'{self.url}?search={search_value}'
            cases.append(
                APIEndpointTestCase(
                    method=self.list_method,
                    url=url,
                    client=self.client,
                    check_points=self.list_check_points + [
                        HttpResponseValueContainCheckPoint(search_value, search_key, self.list_root_json_path)
                    ],
                    response_hooks=self.get_response_hooks()
                )
            )
        return cases
    
    def get_filtered_list_test_cases(self):
        if not self.list_filters:
            return []
        cases = []
        for filter_key, filter_values in self.list_filters.items():
            for filter_value in filter_values:
                url = f'{self.url}?{filter_key}={filter_value}'
                cases.append(
                    APIEndpointTestCase(
                        method=self.list_method,
                        url=url,
                        client=self.client,
                        check_points=self.list_check_points + [
                            HttpResponseValueInListItemsCheckPoint(filter_value, filter_key, self.list_root_json_path)
                        ],
                        response_hooks=self.get_response_hooks()
                    )
                )
        return cases

    def get_filtered_and_searched_list_test_cases(self):
        if not self.list_search or not self.list_filters:
            return []
        cases = []
        for filter_key, filter_values in self.list_filters.items():
            for filter_value in filter_values:
                base_url = f'{self.url}?{filter_key}={filter_value}'
                for search_key, search_value in self.list_search.items():
                    url = f'{base_url}&search={search_value}'
                    cases.append(
                        APIEndpointTestCase(
                            method=self.list_method,
                            url=url,
                            client=self.client,
                            check_points=self.list_check_points + [
                                HttpResponseValueContainCheckPoint(search_value, search_key, self.list_root_json_path),
                                HttpResponseValueInListItemsCheckPoint(filter_value, filter_key, self.list_root_json_path)
                            ],
                            response_hooks=self.get_response_hooks()
                        )
                    )
        return cases

    def get_list_test_cases(self, *args, **kwargs):
        return [APIEndpointTestCase(
            method=self.list_method,
            url=self.url,
            client=self.client,
            check_points=self.list_check_points,
            response_hooks=self.get_response_hooks()
        )]


class RetrieveApiMixin:
    ...


class ClenupMixin:
    should_cleanup_after_test = True


class RestApiCaseSet(
    FakerAsTestCaseMixin,
    CreateApiMixin,
    UpdateApiMixin,
    DeleteApiMixin,
    ListApiMixin,
    RetrieveApiMixin,
    ClenupMixin
):
    faker_class = None
    url = None
    client = None
    retrieve_url = None
    pk_variable = 'id'
    enable = None

    def get_faker_class(self):
        if getattr(self, 'faker_class', None) is None:
            raise AttributeError('`faker_class` is not defined.')
        return self.faker_class

    def get_caseset(self):
        cases = []
        for member_name, member in inspect.getmembers(self):
            if (
                inspect.ismethod(member)
                and member_name.startswith('get_')
                and member_name.endswith('_test_cases')
                and (not self.enable or self.enable in member_name)
            ):
                if _cases := member():
                    cases.extend(_cases)
        return cases

    def clenup(self):
        if self.should_cleanup_after_test:
            print('Start cleanup...')
            for member_name, member in inspect.getmembers(self):
                if (
                    inspect.ismethod(member)
                    and member_name.startswith('clenup_')
                ):
                    member()
                    logger.info(f'Cleanup {member_name} success.')
