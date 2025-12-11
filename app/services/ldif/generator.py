"""LDIF generation module."""
import base64
from typing import List, Union
from .models import LDAPEntry


def is_safe_string(s: str) -> bool:
    """
    Check if a string is safe for LDIF without base64 encoding.
    
    RFC 2849:
    SAFE-INIT-CHAR = %x01-09 / %x0B-0C / %x0E-1F / %x21-39 / %x3B / %x3C-7F
                     ; any value <= 127 decimal except NUL, LF, CR, SPACE, colon, <
    SAFE-CHAR      = %x01-09 / %x0B-0C / %x0E-7F
                     ; any value <= 127 decimal except NUL, LF, CR
    
    Args:
        s: String to check
        
    Returns:
        True if the string is safe for LDIF, False otherwise
    """
    if not s:
        return True

    # Check characters
    for char in s:
        code = ord(char)
        if code > 127 or code == 0 or code == 10 or code == 13:
            return False

    # Check first char
    first_code = ord(s[0])
    # Cannot start with space (32), colon (58), or less-than (60)
    if first_code == 32 or first_code == 58 or first_code == 60:
        return False

    # Check trailing space
    if s[-1] == " ":
        return False

    return True


def encode_value(value: str) -> str:
    """
    Encode a value using base64 for LDIF.
    
    Args:
        value: The value to encode
        
    Returns:
        Base64 encoded string
    """
    encoded_bytes = base64.b64encode(value.encode("utf-8"))
    return encoded_bytes.decode("ascii")


class LDIFGenerator:
    """LDIF format generator."""
    
    @staticmethod
    def generate(entry: Union[LDAPEntry, List[LDAPEntry]]) -> str:
        """
        Generate LDIF output from LDAP entry or entries.
        
        Args:
            entry: Single LDAP entry or list of entries
            
        Returns:
            LDIF formatted string
        """
        if isinstance(entry, list):
            return LDIFGenerator.generate_batch(entry)

        entry.validate()

        lines = []

        # DN
        if is_safe_string(entry.dn):
            lines.append(f"dn: {entry.dn}")
        else:
            lines.append(f"dn:: {encode_value(entry.dn)}")

        # ObjectClasses
        for oc in entry.object_classes:
            if is_safe_string(oc):
                lines.append(f"objectClass: {oc}")
            else:
                lines.append(f"objectClass:: {encode_value(oc)}")

        # Attributes
        for attr, values in entry.attributes.items():
            for val in values:
                if is_safe_string(val):
                    lines.append(f"{attr}: {val}")
                else:
                    lines.append(f"{attr}:: {encode_value(val)}")

        return "\n".join(lines)

    @staticmethod
    def generate_batch(entries: List[LDAPEntry]) -> str:
        """
        Generate LDIF output from multiple entries.
        
        Args:
            entries: List of LDAP entries
            
        Returns:
            LDIF formatted string with all entries
        """
        ldif_outputs = []
        for entry in entries:
            ldif_outputs.append(LDIFGenerator.generate(entry))

        return "\n\n".join(ldif_outputs)
