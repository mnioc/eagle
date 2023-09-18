from eagle.testcase.suitus import HttpTestSuite
from eagle.utils import get_value_from_json_path
from eagle.testcase.check_points import UnitTeseCaseCheckPoint


class Middleware:

    def process(self, pipeline):
        ...


class UnitTestCaseSetContextMiddleware(Middleware):
    def __init__(self, unit_test_case, context_key, json_path):
        self.unit_test_case = unit_test_case
        self.context_key = context_key
        self.json_path = json_path

    def process(self, pipeline):
        self.unit_test_case.execute()
        if response := self.unit_test_case.response:
            value = get_value_from_json_path(response.json(), self.json_path)
            pipeline.context[self.context_key] = value
        super().process(pipeline)


class ReplaceUrlFromContextMiddleware(Middleware):
    def __init__(self, context_key):
        self.context_key = context_key

    def process(self, pipeline):
        _to_replace = r'{' + self.context_key + r'}'
        for test_case in pipeline.cases:
            test_case.request.url = test_case.request.url.replace(
                _to_replace, pipeline.context.get(self.context_key)
            )
            for point in test_case.check_points:
                if isinstance(point, UnitTeseCaseCheckPoint):
                    point.unit_test_case.request.url = point.unit_test_case.request.url.replace(
                        _to_replace, pipeline.context.get(self.context_key)
                    )
        super().process(pipeline)


class HttpTestPipeline(HttpTestSuite):

    def __init__(
        self,
        cases=None,
        pre_execute=None,
        execute_after=None,
    ):
        self.cases = cases
        if self.cases is None:
            self.cases = []
        self.context = {}
        self.pre_execute = pre_execute or []
        self.execute_after = execute_after or []

    def execute(self, *args, **kwagrs) -> None:
        for middleware in self.pre_execute:
            middleware.process(self)
        super().execute(*args, **kwagrs)
        for middleware in self.execute_after:
            middleware.process(self)

    def add_pre_execute(self, middleware):
        self.pre_execute.append(middleware)
        return self

    def add_execute_after(self, middleware):
        self.execute_after.append(middleware)
        return self
