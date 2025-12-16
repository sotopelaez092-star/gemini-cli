# Registry imports all plugins at load time
class PluginRegistry:
    def __init__(self):
        self._plugins = {}

    def register(self, name, plugin_class):
        self._plugins[name] = plugin_class

    def load_plugins(self):
        # Importing plugins here causes cycle
        from plugins.compress_plugin import CompressPlugin
        from plugins.encrypt_plugin import EncryptPlugin

        self.register("compress", CompressPlugin)
        self.register("encrypt", EncryptPlugin)

    def execute(self, plugin_name, **kwargs):
        plugin_class = self._plugins.get(plugin_name)
        if plugin_class:
            plugin = plugin_class()
            return plugin.execute(**kwargs)
        raise ValueError(f"Unknown plugin: {plugin_name}")
