import importlib.util
import logging
import os
from types import ModuleType
from typing import TYPE_CHECKING, List, Optional

from app.lib.connector_base import ConnectorBase
from app.lib.logger import setup_logger

if TYPE_CHECKING:
    from app.lib.bot_manager import BotManager


class ConnectorManager:
    def __init__(self, bot: "BotManager"):
        self.logger = setup_logger(
            "ConnectorManager",
            logging.DEBUG,
            max_bytes=2 * 1024 * 1024,
            backup_count=1,
        )
        self.connector_types: List[str] = self.discover_connector_types()
        self.connectors: dict[str, ConnectorBase] = {}
        self.load_connectors(bot)

    def discover_connector_types(self) -> List[str]:
        """
        Discover all available connector types by listing subdirectories in the 'connectors' directory.
        """
        connectors_base_dir: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../connectors")
        )
        connector_types: List[str] = []

        if not os.path.isdir(connectors_base_dir):
            self.logger.critical(
                f"Connectors base directory {connectors_base_dir} does not exist."
            )
            return connector_types

        for item in os.listdir(connectors_base_dir):
            item_path: str = os.path.join(connectors_base_dir, item)
            if os.path.isdir(item_path):
                connector_types.append(
                    item
                )  # Each subdirectory is considered a connector type
        self.logger.info(
            f"Loading connectors of types: {', '.join(connector_types)}"
        )
        return connector_types

    def load_connector_module(self, path: str) -> Optional[ModuleType]:
        """
        Load a Python module from the given file path.
        """
        try:
            spec = importlib.util.spec_from_file_location(
                "connector_module", path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            return None
        except Exception as e:
            self.logger.exception(f"Failed to load {path}  - error: {e}")

    def load_connectors(self, bot: "BotManager") -> None:
        """
        Load connectors from specified types ('ui', 'chat', or any other discovered type).
        """
        connectors_base_dir: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../connectors")
        )

        # Loop through each specified connector type
        for connector_type in self.connector_types:
            type_dir: str = os.path.join(connectors_base_dir, connector_type)
            if not os.path.isdir(type_dir):
                self.logger.critical(
                    f"Connector type directory {type_dir} does not exist."
                )
                continue

            # Load each connector within the specified type directory
            for connector_name in os.listdir(type_dir):
                connector_path: str = os.path.join(
                    type_dir, connector_name, "main.py"
                )
                if os.path.isfile(connector_path):
                    module = self.load_connector_module(connector_path)
                    if module:
                        # Retrieve the Connector class
                        connector_class = getattr(module, "Connector", None)
                        try:
                            if connector_class:
                                connector_instance = connector_class(bot)
                                if isinstance(
                                    connector_instance, ConnectorBase
                                ):
                                    self.connectors[
                                        f"{connector_type}_{connector_name}"
                                    ] = connector_instance
                                    self.logger.info(
                                        f"Loaded connector: {connector_name} from {connector_type}"
                                    )
                                else:
                                    self.logger.critical(
                                        f"Connector: {connector_name} from {connector_type} does not inherit from ConnectorProtocol class"
                                    )

                            else:
                                self.logger.critical(
                                    f"No Connector class implementing ConnectorProtocol found in {connector_name}"
                                )
                        except Exception as e:
                            self.logger.exception(
                                f"Failed to load module for connector '{connector_name}' from {connector_type} - error: {e}"
                            )

                    else:
                        self.logger.critical(
                            f"Failed to load module for connector '{connector_name}' from {connector_type}"
                        )

    def is_overridden(self, subclass: ConnectorBase, method_name: str) -> bool:
        subclass_method = getattr(subclass, method_name, None)
        base_instance = ConnectorBase(None)  # type: ignore
        parent_method = getattr(base_instance, method_name, None)
        if not subclass_method or not parent_method:
            return False  # Method does not exist in one of the classes
        return subclass_method.__func__ is not parent_method.__func__
