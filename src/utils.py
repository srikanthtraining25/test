def escape_dn_value(value: str) -> str:
    """
    Escapes a value for use in a Distinguished Name (DN) as per RFC 4514.
    """
    if not value:
        return ""

    escaped = ""
    # Characters requiring escaping: , + " \ < > ;
    special_chars = {',', '+', '"', '\\', '<', '>', ';'}
    
    # Leading #
    if value.startswith('#'):
        escaped += '\\' + value[0]
        start_index = 1
    elif value.startswith(' '):
        escaped += '\\' + value[0]
        start_index = 1
    else:
        start_index = 0
        
    for i in range(start_index, len(value)):
        char = value[i]
        if char in special_chars:
            escaped += '\\' + char
        else:
            escaped += char
            
    # Trailing space
    if escaped.endswith(' ') and not escaped.endswith('\\ '):
         # If the last char was space, it wasn't escaped in the loop (unless it was special, but space isn't in special_chars)
         # So we need to escape the last space.
         # But wait, we iterate char by char.
         # The logic above is: if char is special, escape it. Space is not in special_chars.
         # So we just appended space.
         # If it is the last char, we need to replace it with '\ '
         escaped = escaped[:-1] + '\\ '

    return escaped
