"""LDIF utility functions."""


def escape_dn_value(value: str) -> str:
    """
    Escape special characters in DN values according to RFC 4514.
    
    Args:
        value: The DN value to escape
        
    Returns:
        The escaped DN value
    """
    escaped = ""
    for i, char in enumerate(value):
        # Characters that need escaping
        if char in ("#", ",", "+", '"', "\\", "<", ">", ";"):
            escaped += "\\" + char
        elif ord(char) < 32 or ord(char) > 126:
            escaped += "".join([f"\\{byte:02x}" for byte in char.encode("utf-8")])
        else:
            escaped += char
    
    # Handle leading/trailing spaces
    if escaped and escaped[0] == " ":
        escaped = "\\ " + escaped[1:]
    if escaped and escaped[-1] == " ":
        escaped = escaped[:-1] + "\\ "
    
    return escaped


def is_printable_string(value: str) -> bool:
    """Check if a string is printable without encoding."""
    if not value:
        return True
    
    for char in value:
        code = ord(char)
        # Check for non-printable ASCII
        if code < 32 and code not in (9,):  # Allow tab
            return False
        if code > 126:
            return False
    
    return True
