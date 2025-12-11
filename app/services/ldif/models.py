"""LDAP model classes for LDIF generation."""
from typing import List, Dict, Optional
from .utils import escape_dn_value
from .validator import validate_entry


class LDAPEntry:
    """Base LDAP entry class."""
    
    def __init__(
        self,
        rdn: str,
        parent_dn: str,
        object_classes: List[str],
        attributes: Dict[str, List[str]] = None,
    ):
        """
        Initialize an LDAP entry.
        
        Args:
            rdn: Relative Distinguished Name
            parent_dn: Parent DN
            object_classes: List of LDAP object classes
            attributes: Dictionary of attributes (name -> list of values)
        """
        self.rdn = rdn
        self.parent_dn = parent_dn
        self.object_classes = object_classes if object_classes else []
        self.attributes = attributes if attributes else {}

    @property
    def dn(self) -> str:
        """Get the full Distinguished Name."""
        if not self.parent_dn:
            return self.rdn
        return f"{self.rdn},{self.parent_dn}"

    def validate(self) -> None:
        """Validate the entry."""
        validate_entry(self)

    def add_attribute(self, name: str, value: str) -> None:
        """
        Add an attribute value to the entry.
        
        Args:
            name: Attribute name
            value: Attribute value
        """
        if name not in self.attributes:
            self.attributes[name] = []
        self.attributes[name].append(value)


class User(LDAPEntry):
    """LDAP User entry."""
    
    def __init__(
        self,
        uid: str,
        parent_dn: str,
        cn: str,
        sn: str,
        additional_attributes: Dict[str, List[str]] = None,
    ):
        """
        Initialize a User entry.
        
        Args:
            uid: User ID
            parent_dn: Parent DN
            cn: Common Name
            sn: Surname
            additional_attributes: Additional attributes
        """
        attributes = {
            "uid": [uid],
            "cn": [cn],
            "sn": [sn],
        }
        if additional_attributes:
            for k, v in additional_attributes.items():
                if k in attributes:
                    attributes[k].extend(v)
                else:
                    attributes[k] = v

        super().__init__(
            rdn=f"uid={escape_dn_value(uid)}",
            parent_dn=parent_dn,
            object_classes=["top", "person", "organizationalPerson", "inetOrgPerson"],
            attributes=attributes,
        )


class Group(LDAPEntry):
    """LDAP Group entry."""
    
    def __init__(
        self,
        cn: str,
        parent_dn: str,
        members: List[str] = None,
        additional_attributes: Dict[str, List[str]] = None,
    ):
        """
        Initialize a Group entry.
        
        Args:
            cn: Common Name
            parent_dn: Parent DN
            members: List of member DNs
            additional_attributes: Additional attributes
        """
        attributes = {
            "cn": [cn],
            "member": members if members else [],
        }
        if additional_attributes:
            for k, v in additional_attributes.items():
                if k in attributes:
                    attributes[k].extend(v)
                else:
                    attributes[k] = v

        super().__init__(
            rdn=f"cn={escape_dn_value(cn)}",
            parent_dn=parent_dn,
            object_classes=["top", "groupOfNames"],
            attributes=attributes,
        )


class OU(LDAPEntry):
    """LDAP Organizational Unit entry."""
    
    def __init__(
        self,
        name: str,
        parent_dn: str,
        additional_attributes: Dict[str, List[str]] = None,
    ):
        """
        Initialize an OU entry.
        
        Args:
            name: OU name
            parent_dn: Parent DN
            additional_attributes: Additional attributes
        """
        attributes = {
            "ou": [name],
        }
        if additional_attributes:
            for k, v in additional_attributes.items():
                if k in attributes:
                    attributes[k].extend(v)
                else:
                    attributes[k] = v

        super().__init__(
            rdn=f"ou={escape_dn_value(name)}",
            parent_dn=parent_dn,
            object_classes=["top", "organizationalUnit"],
            attributes=attributes,
        )
