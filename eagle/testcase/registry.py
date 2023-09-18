

class RestApiTestCaseRegistry(object):
    def __init__(self):
        self._testcases = {}

    def register(self, testcase):
        self._testcases[testcase.name] = testcase

    def get(self, name):
        return self._testcases.get(name)
    


if __name__ == '__main__':
    ...