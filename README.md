# eagle - HTTP API 接口自动化测试框架

**eagle** 是一款强大的HTTP API接口自动化测试框架，旨在简化和加速API测试过程。它能够自动发现测试用例，支持自动生成正向用例和异常用例，同时内置了多款HTTP认证客户端，使测试变得更加灵活和高效。

## 为什么叫 eagle

*eagle* 意为老鹰，我们希望它能够像鹰眼一样，帮助您更快地发现API的潜在问题，更好地保护您的产品质量。

## eagle 的特性

- **自动发现测试用例：** *eagle* 能够自动搜索和加载指定目录中的单元测试和测试套件，减少了配置的繁琐步骤。

- **内置HTTP认证客户端：** 支持常见的HTTP认证方式，包括基本认证、摘要认证等，轻松应对不同的认证需求。

- **自动生成正向用例：** *eagle* 可以根据API的入参规范自动生成正向测试用例，减少了手工编写用例的工作量。

- **自动构造异常用例：** 除了正向用例，*eagle* 还具备自动生成异常测试用例的能力，帮助您更全面地覆盖API的各种情况。

- **支持多种测试：** *eagle* 支持多种测试套件，包括单元测试、接口测试、性能测试等，满足不同场景的测试需求。

- **支持多种测试报告：** *eagle* 支持多种测试报告，包括HTML报告、Excel报告，满足不同场景的报告需求。

- **支持yaml声明式定义测试用例：** *eagle* 支持yaml格式的测试用例，可以更加简洁地定义测试用例。这对于不会编程的测试人员来说，是一个很好的选择。

- **支持pipeline式执行：** 测试用例可能需要某些上下文环境，*eagle* 支持管道化执行，为测试用例提供完备的上下文管理。


## 安装

你可以使用 pip 安装 eagle:

```python
pip install eagle
```


## 快速开始

### 创建一个测试用例

1. 创建一个 Python 文件，例如 `test_sample.py`。



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

## 贡献
如果你想为 eagle 做出贡献，请查看贡献指南了解更多信息。

## 许可证
本项目采用 MIT 许可证。详细信息请参阅 LICENSE 文件。

## 联系我们
有问题或建议？请在 GitHub 上提交问题。我们欢迎您的反馈和贡献！

## 常见问题
查看常见问题以获取更多信息。

## 版本历史
查看版本历史以了解 eagle 的更新和变更记录。
