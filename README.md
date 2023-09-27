# eagle - HTTP API Automation Testing Framework
eagle is a powerful HTTP API automation testing framework designed to simplify and accelerate the API testing process. It can automatically discover test cases, support the generation of positive and negative test cases, and comes with multiple built-in HTTP authentication clients, making testing more flexible and efficient.

Why is it called eagle?

eagle means an eagle, and we hope it can help you discover potential issues with APIs faster, just like an eagle's eye, and better protect the quality of your product.

## Features of eagle
- Automatic discovery of test cases: eagle can automatically search and load unit tests and test suites in the specified directory, reducing the tedious configuration steps.

- Built-in HTTP authentication clients: Supports common HTTP authentication methods, including basic authentication, digest authentication, etc., to easily meet different authentication requirements.

- Automatic generation of positive test cases: eagle can automatically generate positive test cases based on the API's input specification, reducing the workload of manually writing test cases.

- Automatic generation of negative test cases: In addition to positive test cases, eagle also has the ability to automatically generate negative test cases, helping you comprehensively cover various scenarios of the API.

- Support for multiple types of testing: eagle supports multiple types of test suites, including unit tests, interface tests, performance tests, etc., to meet different testing requirements.

- Support for multiple types of test reports: eagle supports multiple types of test reports, including HTML reports and Excel reports, to meet different reporting requirements.

- Support for declaring test cases in YAML: eagle supports test cases in YAML format, allowing for concise test case definitions. This is a great choice for testers who are not familiar with programming.

- Support for pipeline-style execution: Test cases may require certain context environments. eagle supports pipelined execution, providing complete context management for test cases.



## Installation

You can install eagle using pip:

```python
pip install api_eagle
```


## Getting Started

### Create a Test Case

1. Create a Python file, e.g., test_sample.py.



```python
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

```

## Contributing
If you would like to contribute to eagle, please check the contribution guidelines for more information.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact Us
Have questions or suggestions? Please submit an issue on GitHub. We welcome your feedback and contributions!

## Frequently Asked Questions
Check the FAQ for more information.

## Version History
See the version history for updates and changes to eagle.
