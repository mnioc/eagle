

class Context:

    def __init__(self):
        self._context = {}

    def get(self, key):
        return self._context.get(key)

    def set(self, key, value):
        self._context[key] = value


context = Context()
