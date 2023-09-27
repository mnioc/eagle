import client
from eagle.faker import fields, constraint, Faker
from eagle.testcase import FakerAutoTestSuite
from eagle.testcase import register_test_case
from eagle.testcase.rest_caseset import RestApiCaseSet


class ContainerFaker(Faker):

    name = fields.CharField(allow_blank=False, required=True, allow_null=False, prefix='only_test_')
    type = fields.ChoiceField(allow_blank=False, required=True, allow_null=False, choices=['pallet', 'shipping_container'])
    length = fields.IntegerField(required=True, allow_null=False, min_value=1)
    width = fields.IntegerField(required=True, allow_null=False, min_value=1)
    height = fields.IntegerField(required=True, allow_null=False, min_value=1)
    weight = fields.FloatField(required=False, allow_null=True, min_value=0)
    payload = fields.FloatField(required=False, allow_null=True, min_value=0)
    cost = fields.FloatField(required=False, allow_null=True, min_value=0)
    extended_properties = fields.DictField(
        required=False,
        allow_null=True,
        stack_height=fields.IntegerField(required=False, allow_null=True, min_value=1),
    )

    class Meta:
        relation_constraints = [
            constraint.RelationConstraint(
                condition=constraint.DictValueEqual(key='type', expected='pallet'),
                constraints=[
                    constraint.DictKeyExist(key='extended_properties', default={}),
                    constraint.DictKeyExist(key=['extended_properties', 'stack_height'], default=120),
                    constraint.DictValueNotNull(key=['extended_properties', 'stack_height'], default=120)
                ]
            )
        ]


@register_test_case
class TestContainer(RestApiCaseSet, FakerAutoTestSuite):
    faker_class = ContainerFaker
    url = '/containers/'
    retrieve_url = '/containers/{pk}/'
    client = client.client

    list_filters = {
        'type': ['pallet', 'shipping_container']
    }
    list_search = {
        'name': 'only_test_'
    }
    list_root_json_path = '$.results'
    show_list_response = True
    show_ignore_keys = ['id', 'created', 'district', 'modifiable', 'managedBy']
    list_page_size_query_param = [5, 10]
