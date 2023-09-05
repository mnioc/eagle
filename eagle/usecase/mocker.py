from eagle.usecase.bases import UnitTestCase
from eagle.usecase.assertions import AssertStatusCodeEqual, AssertAllValueEqual


class AutoGenerateTestCaseMetaclass(type):

    def __new__(cls, name, bases, class_attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, class_attrs, **kwargs)
        if not hasattr(new_cls, 'auto_generate_use_case'):
            return new_cls
        r = getattr(new_cls, 'auto_generate_use_case')

        def use_case_func(self, *args, **kwargs):
            case = UnitTestCase(r['client'], 'test_create_container_mock')
            case.build_request(method=r['method'], url=r['url'], json=r['payload'])
            case.register_response_hook('check_status_code', AssertStatusCodeEqual(201))
            case.execute(should_raise=True)

        setattr(new_cls, 'test_create222', use_case_func)

        return new_cls
