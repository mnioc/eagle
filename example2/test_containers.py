import client
from eagle.testcase.check_points import HttpStatusCodeCheckPoint, UnitTeseCaseCheckPoint
from eagle.testcase.suitus import HttpTestSuite
from eagle.testcase.unit import HttpUnitTestCase
from eagle.testcase.generator import TestCaseGenerator
from eagle.testcase.bases import TestCaseRegistry
from eagle.faker import fields, constraint, Faker


class ContainerFaker(Faker):

    name = fields.CharField(allow_blank=False, required=True, allow_null=False)
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

# ContainerFaker.usecases.post('/containers/', HttpStatusCodeCheckPoint(201), client.client).execute()
# ContainerFaker.usecases.put('/containers/', client.client).execute()
# ContainerFaker.usecases.patch('/containers/', client.client)
# ContainerFaker.usecases.delete('/containers/{container_id}/', client.client)
# ContainerFaker.usecases.get('/containers/{container_id}/', client.client)
# ContainerFaker.usecases.filter(type='pallet').list('/containers/{container_id}/', client.client, HttpResponseValueInListItemsCheckPoint())
# ContainerFaker.usecases.search('40HQ').list('/containers/{container_id}/', client.client, HttpResponseValueInListItemsCheckPoint())


t = TestCaseRegistry()
t.register(ContainerFaker.objects.create('/containers/', client.client, [HttpStatusCodeCheckPoint(201)]))

t.register(
    ContainerFaker.objects.delete(
        url='/containers/{container_id}/',
        client=client.client,
        check_points=[
            HttpStatusCodeCheckPoint(204),
            UnitTeseCaseCheckPoint(
                HttpUnitTestCase(
                    method='GET',
                    url='/containers/{container_id}/',
                    client=client.client,
                    check_points=[HttpStatusCodeCheckPoint(404)]
                ),
            )
        ],
        post_url='/containers/',
        context_key='container_id',
        json_path='$.id'
    )
)

# t.register(ContainerFaker.objects.update(url='/containers/{container_id}/',client=client.client,post_url='/containers/',context_key='container_id',json_path='$.id'))

