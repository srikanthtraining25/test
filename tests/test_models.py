"""Tests for LDAP Pydantic models."""

import pytest
from pydantic import ValidationError

from ldap_schema.models import InetOrgPerson, GroupOfNames, OrganizationalUnit


class TestInetOrgPerson:
    """Tests for InetOrgPerson model."""

    def test_valid_inet_org_person(self):
        """Test creating a valid inetOrgPerson instance."""
        person = InetOrgPerson(
            uid="jdoe",
            cn="John Doe",
            sn="Doe",
            mail="jdoe@example.com",
        )

        assert person.uid == "jdoe"
        assert person.cn == "John Doe"
        assert person.sn == "Doe"
        assert person.mail == "jdoe@example.com"

    def test_required_fields_uid(self):
        """Test that uid is required."""
        with pytest.raises(ValidationError) as exc_info:
            InetOrgPerson(cn="John Doe")

        assert "uid" in str(exc_info.value)

    def test_required_fields_cn(self):
        """Test that cn is required."""
        with pytest.raises(ValidationError) as exc_info:
            InetOrgPerson(uid="jdoe")

        assert "cn" in str(exc_info.value)

    def test_optional_fields(self):
        """Test optional fields can be omitted."""
        person = InetOrgPerson(uid="jdoe", cn="John Doe")

        assert person.uid == "jdoe"
        assert person.cn == "John Doe"
        assert person.sn is None
        assert person.mail is None

    def test_telephone_number_alias(self):
        """Test telephoneNumber alias works."""
        person = InetOrgPerson(
            uid="jdoe",
            cn="John Doe",
            telephoneNumber="+1-555-0100",
        )

        assert person.telephone_number == "+1-555-0100"

    def test_object_class_default(self):
        """Test default object classes."""
        person = InetOrgPerson(uid="jdoe", cn="John Doe")

        assert "inetOrgPerson" in person.object_class
        assert "organizationalPerson" in person.object_class
        assert "person" in person.object_class
        assert "top" in person.object_class

    def test_object_class_alias(self):
        """Test objectClass alias works."""
        custom_classes = ["customClass", "top"]
        person = InetOrgPerson(
            uid="jdoe",
            cn="John Doe",
            objectClass=custom_classes,
        )

        assert person.object_class == custom_classes


class TestGroupOfNames:
    """Tests for GroupOfNames model."""

    def test_valid_group_of_names(self):
        """Test creating a valid groupOfNames instance."""
        group = GroupOfNames(
            cn="developers",
            description="Development team",
            member=["uid=user1,ou=people,dc=example,dc=com"],
        )

        assert group.cn == "developers"
        assert group.description == "Development team"
        assert len(group.member) == 1
        assert group.member[0] == "uid=user1,ou=people,dc=example,dc=com"

    def test_required_field_cn(self):
        """Test that cn is required."""
        with pytest.raises(ValidationError) as exc_info:
            GroupOfNames()

        assert "cn" in str(exc_info.value)

    def test_empty_members_default(self):
        """Test members default to empty list."""
        group = GroupOfNames(cn="developers")

        assert group.member == []

    def test_multiple_members(self):
        """Test group with multiple members."""
        members = [
            "uid=user1,ou=people,dc=example,dc=com",
            "uid=user2,ou=people,dc=example,dc=com",
            "uid=user3,ou=people,dc=example,dc=com",
        ]
        group = GroupOfNames(cn="developers", member=members)

        assert len(group.member) == 3
        assert group.member == members

    def test_object_class_default(self):
        """Test default object classes."""
        group = GroupOfNames(cn="developers")

        assert "groupOfNames" in group.object_class
        assert "top" in group.object_class

    def test_object_class_alias(self):
        """Test objectClass alias works."""
        custom_classes = ["groupOfNames", "top"]
        group = GroupOfNames(
            cn="developers",
            objectClass=custom_classes,
        )

        assert group.object_class == custom_classes


class TestOrganizationalUnit:
    """Tests for OrganizationalUnit model."""

    def test_valid_organizational_unit(self):
        """Test creating a valid organizationalUnit instance."""
        ou = OrganizationalUnit(
            ou="people",
            description="People organizational unit",
        )

        assert ou.ou == "people"
        assert ou.description == "People organizational unit"

    def test_required_field_ou(self):
        """Test that ou is required."""
        with pytest.raises(ValidationError) as exc_info:
            OrganizationalUnit()

        assert "ou" in str(exc_info.value)

    def test_optional_description(self):
        """Test description is optional."""
        ou = OrganizationalUnit(ou="people")

        assert ou.ou == "people"
        assert ou.description is None

    def test_object_class_default(self):
        """Test default object classes."""
        ou = OrganizationalUnit(ou="people")

        assert "organizationalUnit" in ou.object_class
        assert "top" in ou.object_class

    def test_object_class_alias(self):
        """Test objectClass alias works."""
        custom_classes = ["organizationalUnit", "top"]
        ou = OrganizationalUnit(
            ou="people",
            objectClass=custom_classes,
        )

        assert ou.object_class == custom_classes

    def test_ou_field_name_not_confused_with_object_class(self):
        """Test ou field is distinct from object_class."""
        ou = OrganizationalUnit(ou="groups")

        assert ou.ou == "groups"
        assert ou.object_class == ["organizationalUnit", "top"]
