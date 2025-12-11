"""Tests for LDAP schema loader."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ldap_schema.schema_loader import SchemaLoader
from ldap_schema.models import InetOrgPerson, GroupOfNames, OrganizationalUnit


@pytest.fixture
def schema_loader():
    """Create a schema loader instance."""
    return SchemaLoader()


@pytest.fixture
def sample_yaml_schema():
    """Create a sample YAML schema configuration."""
    return {
        "inetOrgPerson": {
            "attributes": {
                "uid": {"ldap_name": "uid", "required": True},
                "common_name": {
                    "ldap_name": "cn",
                    "required": True,
                },
                "surname": {"ldap_name": "sn", "required": False},
                "email": {"ldap_name": "mail", "required": False},
            }
        },
        "groupOfNames": {
            "attributes": {
                "common_name": {
                    "ldap_name": "cn",
                    "required": True,
                },
                "description": {
                    "ldap_name": "description",
                    "required": False,
                },
                "members": {"ldap_name": "member", "required": False},
            }
        },
    }


@pytest.fixture
def sample_json_schema():
    """Create a sample JSON schema configuration."""
    return {
        "organizationalUnit": {
            "attributes": {
                "unit_name": {"ldap_name": "ou", "required": True},
                "description": {
                    "ldap_name": "description",
                    "required": False,
                },
            }
        }
    }


class TestSchemaLoaderBasics:
    """Basic schema loader functionality tests."""

    def test_initialization(self, schema_loader):
        """Test schema loader initializes correctly."""
        assert schema_loader.schemas == {}
        assert schema_loader.model_mappings == {}

    def test_register_model(self, schema_loader):
        """Test registering a model."""
        schema_loader.register_model("inetOrgPerson", InetOrgPerson)

        assert "inetOrgPerson" in schema_loader.model_mappings
        assert schema_loader.model_mappings["inetOrgPerson"] == InetOrgPerson

    def test_register_multiple_models(self, schema_loader):
        """Test registering multiple models."""
        schema_loader.register_model("inetOrgPerson", InetOrgPerson)
        schema_loader.register_model("groupOfNames", GroupOfNames)
        schema_loader.register_model("organizationalUnit", OrganizationalUnit)

        assert len(schema_loader.model_mappings) == 3
        assert schema_loader.model_mappings["inetOrgPerson"] == InetOrgPerson
        assert schema_loader.model_mappings["groupOfNames"] == GroupOfNames
        assert (
            schema_loader.model_mappings["organizationalUnit"]
            == OrganizationalUnit
        )


class TestYAMLSchemaLoading:
    """YAML schema loading tests."""

    def test_load_valid_yaml_schema(
        self, schema_loader, sample_yaml_schema
    ):
        """Test loading a valid YAML schema."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)

            assert "inetOrgPerson" in schema_loader.schemas
            assert "groupOfNames" in schema_loader.schemas
            assert len(schema_loader.list_schemas()) == 2
        finally:
            Path(temp_path).unlink()

    def test_load_valid_yml_schema(
        self, schema_loader, sample_yaml_schema
    ):
        """Test loading a valid .yml schema."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)

            assert "inetOrgPerson" in schema_loader.schemas
            assert "groupOfNames" in schema_loader.schemas
        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_yaml_file(self, schema_loader):
        """Test loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            schema_loader.load_schema("/nonexistent/path/schema.yaml")

    def test_load_invalid_yaml_format(self, schema_loader):
        """Test loading invalid YAML raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content:")
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "Failed to parse YAML" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_load_yaml_non_dict(self, schema_loader):
        """Test loading YAML that is not a dict raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(["not", "a", "dict"], f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must contain a dictionary" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()


class TestJSONSchemaLoading:
    """JSON schema loading tests."""

    def test_load_valid_json_schema(self, schema_loader, sample_json_schema):
        """Test loading a valid JSON schema."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(sample_json_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)

            assert "organizationalUnit" in schema_loader.schemas
        finally:
            Path(temp_path).unlink()

    def test_load_invalid_json_format(self, schema_loader):
        """Test loading invalid JSON raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{invalid json content}")
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "Failed to parse JSON" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_load_json_non_dict(self, schema_loader):
        """Test loading JSON that is not a dict raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(["not", "a", "dict"], f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must contain a dictionary" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()


class TestSchemaValidation:
    """Schema structure validation tests."""

    def test_validate_schema_empty_content(self, schema_loader):
        """Test validation fails for empty schema."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump({}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "cannot be empty" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_validate_schema_non_dict_schema(self, schema_loader):
        """Test validation fails when schema is not a dict."""
        invalid_schema = {"mySchema": ["not", "a", "dict"]}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(invalid_schema, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must be a dictionary" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_validate_schema_missing_attributes(self, schema_loader):
        """Test validation fails when attributes are missing."""
        invalid_schema = {"mySchema": {"description": "Missing attributes"}}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(invalid_schema, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must define 'attributes'" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_validate_schema_non_dict_attributes(self, schema_loader):
        """Test validation fails when attributes is not a dict."""
        invalid_schema = {
            "mySchema": {"attributes": ["not", "a", "dict"]}
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(invalid_schema, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must be a dictionary" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_validate_attribute_non_dict(self, schema_loader):
        """Test validation fails when attribute config is not a dict."""
        invalid_schema = {
            "mySchema": {
                "attributes": {
                    "uid": "not a dict",
                }
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(invalid_schema, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must be a dictionary" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_validate_attribute_missing_ldap_name(self, schema_loader):
        """Test validation fails when ldap_name is missing."""
        invalid_schema = {
            "mySchema": {
                "attributes": {
                    "uid": {"required": True},
                }
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(invalid_schema, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "must have 'ldap_name' mapping" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()


class TestUnsupportedFileFormat:
    """Tests for unsupported file formats."""

    def test_unsupported_file_format(self, schema_loader):
        """Test loading unsupported file format raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", delete=False
        ) as f:
            f.write("<schema></schema>")
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                schema_loader.load_schema(temp_path)
            assert "Unsupported file format" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()


class TestAttributeMappings:
    """Tests for attribute mappings."""

    def test_get_attribute_mapping_valid(
        self, schema_loader, sample_yaml_schema
    ):
        """Test getting a valid attribute mapping."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)
            mapping = schema_loader.get_attribute_mapping(
                "inetOrgPerson", "uid"
            )
            assert mapping == "uid"
        finally:
            Path(temp_path).unlink()

    def test_get_attribute_mapping_common_name(
        self, schema_loader, sample_yaml_schema
    ):
        """Test getting mapping for common_name."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)
            mapping = schema_loader.get_attribute_mapping(
                "inetOrgPerson", "common_name"
            )
            assert mapping == "cn"
        finally:
            Path(temp_path).unlink()

    def test_get_attribute_mapping_nonexistent_schema(self, schema_loader):
        """Test getting mapping for nonexistent schema returns None."""
        mapping = schema_loader.get_attribute_mapping(
            "nonexistent", "uid"
        )
        assert mapping is None

    def test_get_attribute_mapping_nonexistent_attribute(
        self, schema_loader, sample_yaml_schema
    ):
        """Test getting mapping for nonexistent attribute returns None."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)
            mapping = schema_loader.get_attribute_mapping(
                "inetOrgPerson", "nonexistent"
            )
            assert mapping is None
        finally:
            Path(temp_path).unlink()


class TestDataValidation:
    """Tests for data validation against registered schemas."""

    def test_validate_data_valid_inet_org_person(self, schema_loader):
        """Test validating valid inetOrgPerson data."""
        schema_loader.register_model("inetOrgPerson", InetOrgPerson)

        data = {"uid": "jdoe", "cn": "John Doe", "mail": "jdoe@example.com"}
        result = schema_loader.validate_data("inetOrgPerson", data)

        assert isinstance(result, InetOrgPerson)
        assert result.uid == "jdoe"
        assert result.cn == "John Doe"

    def test_validate_data_valid_group_of_names(self, schema_loader):
        """Test validating valid groupOfNames data."""
        schema_loader.register_model("groupOfNames", GroupOfNames)

        data = {
            "cn": "developers",
            "description": "Dev team",
            "member": ["uid=user1,ou=people,dc=example,dc=com"],
        }
        result = schema_loader.validate_data("groupOfNames", data)

        assert isinstance(result, GroupOfNames)
        assert result.cn == "developers"
        assert len(result.member) == 1

    def test_validate_data_valid_organizational_unit(self, schema_loader):
        """Test validating valid organizationalUnit data."""
        schema_loader.register_model("organizationalUnit", OrganizationalUnit)

        data = {"ou": "people", "description": "People OU"}
        result = schema_loader.validate_data("organizationalUnit", data)

        assert isinstance(result, OrganizationalUnit)
        assert result.ou == "people"

    def test_validate_data_unregistered_schema(self, schema_loader):
        """Test validating against unregistered schema raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            schema_loader.validate_data(
                "unregistered", {"uid": "test"}
            )
        assert "not registered" in str(exc_info.value)

    def test_validate_data_invalid_data(self, schema_loader):
        """Test validating invalid data raises ValidationError."""
        schema_loader.register_model("inetOrgPerson", InetOrgPerson)

        with pytest.raises(ValidationError):
            schema_loader.validate_data("inetOrgPerson", {})

    def test_validate_data_missing_required_field(self, schema_loader):
        """Test validating data missing required field raises error."""
        schema_loader.register_model("inetOrgPerson", InetOrgPerson)

        with pytest.raises(ValidationError) as exc_info:
            schema_loader.validate_data("inetOrgPerson", {"uid": "jdoe"})

        assert "cn" in str(exc_info.value)


class TestSchemaSelection:
    """Tests for schema selection and retrieval."""

    def test_get_schema(self, schema_loader, sample_yaml_schema):
        """Test getting a schema by name."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)
            schema = schema_loader.get_schema("inetOrgPerson")

            assert schema is not None
            assert "attributes" in schema
        finally:
            Path(temp_path).unlink()

    def test_get_nonexistent_schema(self, schema_loader):
        """Test getting nonexistent schema returns None."""
        schema = schema_loader.get_schema("nonexistent")
        assert schema is None

    def test_list_schemas(self, schema_loader, sample_yaml_schema):
        """Test listing all loaded schemas."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            temp_path = f.name

        try:
            schema_loader.load_schema(temp_path)
            schemas = schema_loader.list_schemas()

            assert "inetOrgPerson" in schemas
            assert "groupOfNames" in schemas
            assert len(schemas) == 2
        finally:
            Path(temp_path).unlink()

    def test_list_schemas_empty(self, schema_loader):
        """Test listing schemas when none are loaded."""
        schemas = schema_loader.list_schemas()
        assert schemas == []


class TestMultipleSchemaFiles:
    """Tests for loading multiple schema files."""

    def test_load_multiple_schema_files(
        self, schema_loader, sample_yaml_schema, sample_json_schema
    ):
        """Test loading schemas from multiple files."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(sample_yaml_schema, f)
            yaml_path = f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(sample_json_schema, f)
            json_path = f.name

        try:
            schema_loader.load_schema(yaml_path)
            schema_loader.load_schema(json_path)

            assert "inetOrgPerson" in schema_loader.schemas
            assert "groupOfNames" in schema_loader.schemas
            assert "organizationalUnit" in schema_loader.schemas
            assert len(schema_loader.list_schemas()) == 3
        finally:
            Path(yaml_path).unlink()
            Path(json_path).unlink()
