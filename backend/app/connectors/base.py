"""Base connector interface and registry."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd


class ConnectorBase(ABC):
    """Abstract base class for all connectors."""
    
    # Connector metadata
    name: str = "base"
    display_name: str = "Base Connector"
    description: str = ""
    version: str = "1.0.0"
    supported_modes: List[str] = ["read", "write"]
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize connector with optional configuration."""
        self.config = config or {}
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the system."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the system."""
        pass
    
    @abstractmethod
    async def get_schema(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover and return schema information.
        
        Args:
            model_name: Optional specific model to get schema for
            
        Returns:
            Dict containing models and their field definitions
        """
        pass
    
    @abstractmethod
    async def extract(
        self,
        model_name: str,
        filters: Dict[str, Any] = None,
        limit: int = None
    ) -> pd.DataFrame:
        """
        Extract data from the source system.
        
        Args:
            model_name: Name of model/table to extract
            filters: Optional filters to apply
            limit: Maximum records to extract
            
        Returns:
            DataFrame containing extracted data
        """
        pass
    
    @abstractmethod
    async def push(
        self,
        model_name: str,
        data: pd.DataFrame,
        mode: str = "create"
    ) -> Dict[str, Any]:
        """
        Push data to the target system.
        
        Args:
            model_name: Name of model/table to push to
            data: DataFrame containing records to push
            mode: Operation mode - 'create', 'update', or 'upsert'
            
        Returns:
            Dict containing results (success count, failures, etc.)
        """
        pass
    
    def validate_config(self) -> List[str]:
        """
        Validate connector configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        return []
    
    @property
    def is_connected(self) -> bool:
        """Check if connector is currently connected."""
        return self._connected
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "supported_modes": self.supported_modes,
            "is_connected": self.is_connected
        }


class CSVConnector(ConnectorBase):
    """Connector for CSV file operations."""
    
    name = "csv"
    display_name = "CSV File"
    description = "Read and write CSV files"
    supported_modes = ["read", "write"]
    
    async def connect(self) -> bool:
        """CSV doesn't require connection."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """CSV doesn't require disconnection."""
        self._connected = False
    
    async def get_schema(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Schema discovery for CSV is done via file parsing."""
        return {"models": [], "message": "Use file upload for CSV schema discovery"}
    
    async def extract(
        self,
        model_name: str,
        filters: Dict[str, Any] = None,
        limit: int = None
    ) -> pd.DataFrame:
        """CSV extraction is handled by FileParser."""
        return pd.DataFrame()
    
    async def push(
        self,
        model_name: str,
        data: pd.DataFrame,
        mode: str = "create"
    ) -> Dict[str, Any]:
        """Write DataFrame to CSV file."""
        file_path = self.config.get("output_path", f"{model_name}.csv")
        data.to_csv(file_path, index=False)
        return {
            "success": True,
            "file_path": file_path,
            "records_written": len(data)
        }


class ConnectorRegistry:
    """Registry for managing available connectors."""
    
    _connectors: Dict[str, type] = {}
    
    @classmethod
    def register(cls, connector_class: type) -> None:
        """Register a connector class."""
        if hasattr(connector_class, 'name'):
            cls._connectors[connector_class.name] = connector_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a connector class by name."""
        return cls._connectors.get(name)
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        """List all registered connectors."""
        return [
            {
                "name": conn.name,
                "display_name": conn.display_name,
                "description": conn.description,
                "supported_modes": conn.supported_modes
            }
            for conn in cls._connectors.values()
        ]
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any] = None) -> Optional[ConnectorBase]:
        """Create a connector instance."""
        connector_class = cls.get(name)
        if connector_class:
            return connector_class(config)
        return None


# Register built-in connectors
ConnectorRegistry.register(CSVConnector)
