import client
from eagle.testcase import FakerAutoTestSuite, register_test_case
from eagle.faker import fields, Faker
from eagle.testcase.rest_caseset import CreateApiMixin


class UserFaker(Faker):

    name = fields.CharField(allow_blank=False, required=True, allow_null=False)
    age = fields.IntegerField(required=True, allow_null=False, min_value=1)
    sex = fields.ChoiceField(allow_blank=False, required=True, allow_null=False, choices=['0', '1'])
    email = fields.EmailField(required=True, allow_null=False, allow_blank=False)
    phone = fields.CharField(required=True, allow_null=False, allow_blank=False, min_length=11, max_length=11)
    address = fields.CharField(required=True, allow_null=False, allow_blank=False, min_length=1, max_length=255)


"""
How to use:
>>> faker = UserFaker()
>>> faker.valid_data
{
    'name': 'Tom',
    'age': 18,
    'sex': '0',
    'email': 'tom@email.com',
    'phone': '12345678901',
    'address': 'xxx'
}
>>> faker.invalid_data
{
    'name': '',  # it not allow blank !!!
    'age': 18,
    'sex': '0',
    'email': 'tom@email.com',
    'phone': '12345678901',
    'address': 'xxx'
}
"""

# Auto generate test cases: POST {client.endpoint}/users/
# Your API should accept a JSON object with the following fields:
#     - name: string, required, max length 255
#     - age: integer, required, min value 1
#     - sex: string, required, enum: ['0', '1']
#     - email: string, required, valid email address
#     - phone: string, required, length 11
#     - address: string, required, max length 255
# And then `UserFaker` will auto generate valid and invalid data for you.


@register_test_case
class TestCreateUser(CreateApiMixin, FakerAutoTestSuite):
    faker_class = UserFaker
    client = client.client
    url = '/users/'

    # You can also customize the check points.
    # create_valid_check_points = [HttpStatusCodeEqual(201)]

    # You can also customize the check points.
    # create_invalid_check_points = [HttpStatusCodeEqual(400)]
