
class TestCaseRegistry:
    def __init__(self):
        self.test_cases = []

    def register(self, test_case_cls):
        self.test_cases.append(test_case_cls)

    def get_test_cases(self):
        return self.test_cases


registry = TestCaseRegistry()


def register_test_case(test_case_cls):
    test_case = test_case_cls
    if isinstance(test_case_cls, type):
        test_case = test_case_cls()
    registry.register(test_case)
