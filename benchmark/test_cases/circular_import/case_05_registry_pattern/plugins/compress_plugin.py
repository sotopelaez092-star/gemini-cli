import zlib
from plugins.base_plugin import BasePlugin

class CompressPlugin(BasePlugin):
    def execute(self, data, **kwargs):
        if isinstance(data, str):
            data = data.encode()
        compressed = zlib.compress(data)
        return compressed.hex()
