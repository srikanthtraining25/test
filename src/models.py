from typing import List, Dict, Optional
from src.validator import validate_entry
from src.utils import escape_dn_value

class LDAPEntry:
    def __init__(self, rdn: str, parent_dn: str, object_classes: List[str], attributes: Dict[str, List[str]] = None):
        self.rdn = rdn
        self.parent_dn = parent_dn
        self.object_classes = object_classes if object_classes else []
        self.attributes = attributes if attributes else {}

    @property
    def dn(self) -> str:
        if not self.parent_dn:
            return self.rdn
        return f"{self.rdn},{self.parent_dn}"

    def validate(self):
        validate_entry(self)

    def add_attribute(self, name: str, value: str):
        if name not in self.attributes:
            self.attributes[name] = []
        self.attributes[name].append(value)

class User(LDAPEntry):
    def __init__(self, uid: str, parent_dn: str, cn: str, sn: str, additional_attributes: Dict[str, List[str]] = None):
        attributes = {
            "uid": [uid],
            "cn": [cn],
            "sn": [sn]
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
            attributes=attributes
        )

class Group(LDAPEntry):
    def __init__(self, cn: str, parent_dn: str, members: List[str] = None, additional_attributes: Dict[str, List[str]] = None):
        attributes = {
            "cn": [cn],
            "member": members if members else []
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
            attributes=attributes
        )

class OU(LDAPEntry):
    def __init__(self, name: str, parent_dn: str, additional_attributes: Dict[str, List[str]] = None):
        attributes = {
            "ou": [name]
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
            attributes=attributes
        )
