import importlib.util
import logging
import os
from types import ModuleType
from typing import TYPE_CHECKING, List, Optional

from app.lib.logger import setup_logger
from app.lib.plugins.plugin_base import PluginBase

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class PluginManager:
    def __init__(self, bot: "BotManager"):
        self.logger = setup_logger(
            "PluginManager",
            logging.DEBUG,
        )
        self.dev_mode: bool = bot.dev_mode
        self.plugin_types: List[str] = self.discover_plugin_types()
        self.plugins: dict[str, PluginBase] = {}
        self.load_plugins(bot)

    def discover_plugin_types(self) -> List[str]:
        """
        Discover all available plugin types by listing subdirectories in the 'plugins' directory.
        """
        plugins_base_dir: str = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                (
                    "../../../plugins"
                    if self.dev_mode
                    else "../../../../plugins"
                ),
            )
        )
        plugin_types: List[str] = []

        if not os.path.isdir(plugins_base_dir):
            self.logger.critical(
                f"Plugins base directory {plugins_base_dir} does not exist."
            )
            return plugin_types

        for item in os.listdir(plugins_base_dir):
            item_path: str = os.path.join(plugins_base_dir, item)
            if os.path.isdir(item_path):
                plugin_types.append(
                    item
                )  # Each subdirectory is considered a plugin type
        self.logger.info(f"Loading plugins of types: {', '.join(plugin_types)}")
        return plugin_types

    def load_plugin_module(self, path: str) -> Optional[ModuleType]:
        """
        Load a Python module from the given file path.
        """
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            return None
        except Exception as e:
            self.logger.exception(f"Failed to load {path}  - error: {e}")

    def load_plugins(self, bot: "BotManager") -> None:
        """
        Load plugins from specified types ('ui', 'chat', or any other discovered type).
        """
        plugins_base_dir: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../plugins")
        )

        # Loop through each specified plugin type
        for plugin_type in self.plugin_types:
            type_dir: str = os.path.join(plugins_base_dir, plugin_type)
            if not os.path.isdir(type_dir):
                self.logger.critical(
                    f"Plugin type directory {type_dir} does not exist."
                )
                continue

            # Load each plugin within the specified type directory
            for plugin_name in os.listdir(type_dir):
                plugin_path: str = os.path.join(
                    type_dir, plugin_name, "main.py"
                )
                if os.path.isfile(plugin_path):
                    module = self.load_plugin_module(plugin_path)
                    if module:
                        # Retrieve the Plugin class
                        plugin_class = getattr(module, "Plugin", None)
                        try:
                            if plugin_class:
                                plugin_instance = plugin_class(bot, plugin_name)
                                if isinstance(plugin_instance, PluginBase):
                                    self.plugins[
                                        f"{plugin_type}_{plugin_name}"
                                    ] = plugin_instance
                                    self.logger.info(
                                        f"Loaded plugin: {plugin_name} from {plugin_type}"
                                    )
                                else:
                                    self.logger.critical(
                                        f"Plugin: {plugin_name} from {plugin_type} does not inherit from PluginProtocol class"
                                    )

                            else:
                                self.logger.critical(
                                    f"No Plugin class implementing PluginProtocol found in {plugin_name}"
                                )
                        except Exception as e:
                            self.logger.exception(
                                f"Failed to load module for plugin '{plugin_name}' from {plugin_type} - error: {e}"
                            )

                    else:
                        self.logger.critical(
                            f"Failed to load module for plugin '{plugin_name}' from {plugin_type}"
                        )

    def is_overridden(self, subclass: PluginBase, method_name: str) -> bool:
        subclass_method = getattr(subclass, method_name, None)
        base_instance = PluginBase(None, "none")  # type: ignore
        parent_method = getattr(base_instance, method_name, None)
        if not subclass_method or not parent_method:
            return False  # Method does not exist in one of the classes
        return subclass_method.__func__ is not parent_method.__func__
