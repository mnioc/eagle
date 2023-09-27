import inspect
from eagle.logger import logger


class LogCheckPointMetaclass(type):

    def __new__(cls, name, bases, class_attrs, **kwargs):
        new_cls = super().__new__(cls, name, bases, class_attrs, **kwargs)
        if not inspect.isabstract(new_cls):
            original_call = new_cls.__call__

            def new_call(self, *args, **kwargs):
                result = original_call(self, *args, **kwargs)
                if not self.failed:
                    logger.info(f'check: {self._name} | SUCCESS')
                else:
                    logger.error(f'check: {self._name} | FAILURE | {self.error_message}')
                return result
            new_cls.__call__ = new_call
        return new_cls


class CheckPoint(metaclass=LogCheckPointMetaclass):

    _name = ''
    failed = False
    error_message = ''

    def __call__(self, *args, **kwargs):
        pass

    def do_fail(self, error_message: str = None):
        self.failed = True
        self.error_message = error_message or self.error_message
