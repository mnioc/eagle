import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
# print(sys.path)
import client
from eagle.usecase.bases import UnitTestCase
from eagle.usecase.assertions import AssertStatusCodeEqual, AssertAllValueEqual
from eagle.http.hooks import show_response_table, set_context_from_response
from eagle.usecase.suitus import TestSuitus
from eagle.context import context


class TestContainers(TestSuitus):

    payload = {
        'name': '__20GP',
        'type': 'shipping_container',
        'length': 5925,
        'width': 2340,
        'height': 2379,
        'weight': 20000,
        'payload': 22100,
        'cost': 200
    }

    auto_generate_use_case = {
        'method': 'POST',
        'url': '/containers/',
        'payload': payload,
        'client': client.client,
        'response_hooks': {
            'check_status_code': AssertStatusCodeEqual(201),
        }
    }

    def test_create(self):
        case = UnitTestCase(client.client, 'test_create_container')
        case.build_request(method='POST', url='/containers/', json=self.payload)
        case.register_response_hook('check_status_code', AssertStatusCodeEqual(201))
        case.register_response_hook(
            'set_context',
            set_context_from_response,
            hook_kwargs={
                'context_key': 'container_id',
                'json_path': '$.id'
            }
        )
        case.execute(should_raise=True)

    # def test_update(self):
    #     case = UnitTestCase(client.client, 'test_update_container')
    #     container_id = context.get('container_id')
    #     data = self.payload.copy()
    #     data['name'] = '__20GP_updated'
    #     case.build_request(method='PUT', url=f'/containers/{container_id}/', json=data)
    #     case.register_response_hook('check_status_code', AssertStatusCodeEqual(200))
    #     case.register_response_hook('check_name_updated', AssertAllValueEqual('name', '__20GP_updated', '$'))
    #     case.execute(should_raise=True)

    def test_list(self):
        case = UnitTestCase(client.client, 'test_list_containers')
        case.build_request(method='GET', url='/containers/',)
        case.register_response_hook('show_table', show_response_table, hook_kwargs={'response_data_json_path': '$'})
        case.execute(should_raise=True)
