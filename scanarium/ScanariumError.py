import uuid

from .MessageFormatter import MessageFormatter


class ScanariumError(RuntimeError):
    def __init__(self, code, template, parameters={}, private_parameters={},
                 *args, **kwargs):
        super(ScanariumError, self).__init__(*args, **kwargs)
        self.code = code
        self.template = template
        self.parameters = parameters
        self.private_parameters = private_parameters
        self.message = MessageFormatter().format_message(
            self.template, self.parameters)
        self.uuid = uuid.uuid4()
