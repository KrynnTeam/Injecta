"""
Injecta — Dynamic plugin loader
"""
import importlib
import inspect
import os
import pkgutil
from typing import Any, Dict, List, Optional, Type


class BasePlugin:
    name: str = ""
    description: str = ""
    version: str = "1.0"
    author: str = "Kael / Krynn Team"

    def initialize(self, engine) -> None: ...

    def on_scan_start(self, url: str) -> None: ...

    def on_scan_complete(self, url: str, results: Dict[str, Any]) -> None: ...

    def on_payload(self, payload: str, dbms: str) -> str:
        return payload

    def on_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return result


class PluginLoader:
    def __init__(self, config, logger):
        self.config = config
        self.log = logger
        self.plugins: List[BasePlugin] = []
        self._plugin_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

    def discover(self) -> List[str]:
        found = []
        if not os.path.isdir(self._plugin_dir):
            return found
        for importer, modname, ispkg in pkgutil.iter_modules([self._plugin_dir]):
            if modname not in ("__init__", "loader", "base"):
                found.append(modname)
        return found

    def load(self, plugin_name: str) -> Optional[BasePlugin]:
        try:
            mod = importlib.import_module(f"injecta.plugins.{plugin_name}")
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    instance = obj()
                    self.log.ok(f"Plugin loaded: {instance.name} v{instance.version}")
                    return instance
        except Exception as e:
            self.log.error(f"Failed to load plugin {plugin_name}: {e}")
        return None

    def load_all(self) -> List[BasePlugin]:
        self.plugins = []
        for name in self.discover():
            plugin = self.load(name)
            if plugin:
                self.plugins.append(plugin)
        self.log.info(f"Loaded {len(self.plugins)} plugin(s)")
        return self.plugins

    def register(self, plugin: BasePlugin) -> None:
        self.plugins.append(plugin)
        self.log.ok(f"Plugin registered: {plugin.name}")

    def get_hook_handlers(self, hook: str) -> List[BasePlugin]:
        handlers = []
        for p in self.plugins:
            method = getattr(p, hook, None)
            if method and not getattr(method, "_is_base", False) and callable(method):
                handlers.append(p)
        return handlers

    def apply_payload_hooks(self, payload: str, dbms: str) -> str:
        for p in self.plugins:
            payload = p.on_payload(payload, dbms)
        return payload
