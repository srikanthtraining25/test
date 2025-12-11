"""LDIF validation functions."""
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import LDAPEntry


def validate_dn(dn: str) -> bool:
    """
    Validates a Distinguished Name (DN) string against a simplified RFC 4514 pattern.
    Handles escaped characters correctly.
    """
    if not dn:
        return False
    
    # We need to split by comma, but respect escapes.
    parts = []
    current_part = ""
    escaped = False
    
    for char in dn:
        if escaped:
            current_part += char
            escaped = False
        elif char == '\\':
            escaped = True
            current_part += char
        elif char == ',':
            parts.append(current_part)
            current_part = ""
        else:
            current_part += char
            
    if escaped:
        # DN ended with a single backslash
        return False
        
    parts.append(current_part)
    
    # Pattern: key=value
    part_pattern = r'^[a-zA-Z0-9-]+=.*$' 
    
    for part in parts:
        part = part.strip()
        if not part: 
            # Empty part means double comma or trailing comma, which is invalid
             return False
             
        if not re.match(part_pattern, part):
            return False
            
    return True


def validate_attribute_name(name: str) -> bool:
    """
    Validates an attribute name (descriptors).
    RFC 4512: keystring = leadkeychar *keychar
    leadkeychar = "a"-"z" / "A"-"Z"
    keychar = "a"-"z" / "A"-"Z" / "0"-"9" / "-"
    """
    pattern = r'^[a-zA-Z][a-zA-Z0-9-]*$'
    return bool(re.match(pattern, name))


def validate_entry(entry: "LDAPEntry") -> None:
    """
    Validate an LDAP entry.
    
    Args:
        entry: The LDAP entry to validate
        
    Raises:
        ValueError: If the entry is invalid
    """
    if not validate_dn(entry.dn):
        raise ValueError(f"Invalid DN: {entry.dn}")
    
    for obj_class in entry.object_classes:
        # object class names follow OID or keystring rules. We assume keystring for names.
        if not validate_attribute_name(obj_class):
             raise ValueError(f"Invalid objectClass: {obj_class}")
             
    for attr_name, values in entry.attributes.items():
        if not validate_attribute_name(attr_name):
            raise ValueError(f"Invalid attribute name: {attr_name}")
            
        # We assume values are strings. If they are binary, they should be bytes.
        # Implementation detail: we'll check if list.
        if not isinstance(values, list):
             raise ValueError(f"Attribute {attr_name} values must be a list")
