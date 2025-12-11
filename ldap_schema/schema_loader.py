"""LDAP schema configuration loader supporting YAML and JSON."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml
from pydantic import BaseModel, ValidationError


class SchemaLoader:
    """Loads and validates LDAP schema configurations from YAML/JSON files."""

    def __init__(self):
        """Initialize the schema loader."""
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.model_mappings: Dict[str, Type[BaseModel]] = {}

    def register_model(
        self, schema_name: str, model_class: Type[BaseModel]
    ) -> None:
        """Register a Pydantic model for a schema.

        Args:
            schema_name: Name of the schema (e.g., 'inetOrgPerson')
            model_class: Pydantic model class for validation
        """
        self.model_mappings[schema_name] = model_class

    def load_schema(self, file_path: str) -> None:
        """Load schema configuration from YAML or JSON file.

        Args:
            file_path: Path to the schema configuration file

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported or content is invalid
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            content = self._load_yaml(path)
        elif suffix == ".json":
            content = self._load_json(path)
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. Use .yaml, .yml, or .json"
            )

        self._validate_schema_structure(content)
        self._store_schema(content)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            ValueError: If YAML parsing fails
        """
        try:
            with open(path, "r") as f:
                content = yaml.safe_load(f)
                if not isinstance(content, dict):
                    raise ValueError("Schema file must contain a dictionary")
                return content
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file: {e}")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file.

        Args:
            path: Path to JSON file

        Returns:
            Parsed JSON content as dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            with open(path, "r") as f:
                content = json.load(f)
                if not isinstance(content, dict):
                    raise ValueError("Schema file must contain a dictionary")
                return content
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file: {e}")

    def _validate_schema_structure(self, content: Dict[str, Any]) -> None:
        """Validate the structure of the schema configuration.

        Args:
            content: Parsed schema content

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not content:
            raise ValueError("Schema configuration cannot be empty")

        for schema_name, schema_config in content.items():
            if not isinstance(schema_config, dict):
                raise ValueError(
                    f"Schema '{schema_name}' must be a dictionary"
                )

            if "attributes" not in schema_config:
                raise ValueError(
                    f"Schema '{schema_name}' must define 'attributes'"
                )

            attributes = schema_config["attributes"]
            if not isinstance(attributes, dict):
                raise ValueError(
                    f"Attributes in schema '{schema_name}' must be a dictionary"
                )

            for attr_name, attr_config in attributes.items():
                if not isinstance(attr_config, dict):
                    raise ValueError(
                        f"Attribute '{attr_name}' in schema '{schema_name}' "
                        "must be a dictionary"
                    )

                if "ldap_name" not in attr_config:
                    raise ValueError(
                        f"Attribute '{attr_name}' in schema '{schema_name}' "
                        "must have 'ldap_name' mapping"
                    )

    def _store_schema(self, content: Dict[str, Any]) -> None:
        """Store parsed schema configuration.

        Args:
            content: Parsed schema content
        """
        self.schemas.update(content)

    def validate_data(
        self, schema_name: str, data: Dict[str, Any]
    ) -> BaseModel:
        """Validate data against a registered schema.

        Args:
            schema_name: Name of the schema to validate against
            data: Data to validate

        Returns:
            Validated Pydantic model instance

        Raises:
            ValueError: If schema is not registered
            ValidationError: If data validation fails
        """
        if schema_name not in self.model_mappings:
            raise ValueError(f"Schema '{schema_name}' is not registered")

        model_class = self.model_mappings[schema_name]
        return model_class(**data)

    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get schema configuration by name.

        Args:
            schema_name: Name of the schema

        Returns:
            Schema configuration dictionary or None if not found
        """
        return self.schemas.get(schema_name)

    def list_schemas(self) -> list:
        """List all loaded schema names.

        Returns:
            List of schema names
        """
        return list(self.schemas.keys())

    def get_attribute_mapping(
        self, schema_name: str, attribute_name: str
    ) -> Optional[str]:
        """Get LDAP attribute name mapping for a schema attribute.

        Args:
            schema_name: Name of the schema
            attribute_name: Name of the attribute in the schema

        Returns:
            LDAP attribute name or None if not found
        """
        schema = self.get_schema(schema_name)
        if not schema or "attributes" not in schema:
            return None

        attr_config = schema["attributes"].get(attribute_name)
        if not attr_config:
            return None

        return attr_config.get("ldap_name")
