import base64
from plugins.base_plugin import BasePlugin

class EncryptPlugin(BasePlugin):
    def execute(self, data, **kwargs):
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()
