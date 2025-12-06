"""Connector registry for discovering and managing connectors."""

from typing import Any, Dict, List, Optional, Type

from app.connectors.base import ConnectorBase, ConnectorRegistry


def get_available_connectors() -> List[Dict[str, Any]]:
    """
    Get list of all available connectors.
    
    Returns:
        List of connector metadata dictionaries
    """
    return ConnectorRegistry.list_all()


def get_connector(name: str, config: Dict[str, Any] = None) -> Optional[ConnectorBase]:
    """
    Get a connector instance by name.
    
    Args:
        name: Connector name (e.g., 'csv', 'zoho', 'odoo')
        config: Optional configuration dictionary
        
    Returns:
        Connector instance or None if not found
    """
    return ConnectorRegistry.create(name, config)


def register_connector(connector_class: Type[ConnectorBase]) -> None:
    """
    Register a new connector class.
    
    Args:
        connector_class: Connector class to register
    """
    ConnectorRegistry.register(connector_class)


def connector_exists(name: str) -> bool:
    """
    Check if a connector with the given name exists.
    
    Args:
        name: Connector name
        
    Returns:
        True if connector exists
    """
    return ConnectorRegistry.get(name) is not None


# Import built-in connectors to register them
from app.connectors.csv_connector import CSVXLSXConnector  # noqa: F401, E402


__all__ = [
    "get_available_connectors",
    "get_connector",
    "register_connector",
    "connector_exists",
    "ConnectorRegistry",
]
