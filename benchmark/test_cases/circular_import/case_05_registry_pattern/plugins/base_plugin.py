from abc import ABC, abstractmethod
from plugins import registry  # Imports the global registry

class BasePlugin(ABC):
    def __init__(self):
        self.registry = registry  # Reference to global registry

    @abstractmethod
    def execute(self, **kwargs):
        pass

    def chain_to(self, plugin_name, **kwargs):
        """Chain execution to another plugin."""
        return self.registry.execute(plugin_name, **kwargs)
