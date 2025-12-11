"""LDIF validation functions."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import LDAPEntry


def validate_entry(entry: "LDAPEntry") -> None:
    """
    Validate an LDAP entry.
    
    Args:
        entry: The LDAP entry to validate
        
    Raises:
        ValueError: If the entry is invalid
    """
    if not entry.dn:
        raise ValueError("Entry DN cannot be empty")
    
    if not entry.object_classes:
        raise ValueError("Entry must have at least one object class")
    
    # Validate RDN is not empty
    if not entry.rdn:
        raise ValueError("Entry RDN cannot be empty")
