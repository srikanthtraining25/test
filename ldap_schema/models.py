"""Pydantic models for LDAP entities."""

from typing import Optional, List
from pydantic import BaseModel, Field


class InetOrgPerson(BaseModel):
    """LDAP inetOrgPerson entity model."""

    uid: str = Field(..., description="User unique identifier")
    cn: str = Field(..., description="Common name")
    sn: Optional[str] = Field(None, description="Surname")
    mail: Optional[str] = Field(None, description="Email address")
    telephone_number: Optional[str] = Field(
        None, description="Telephone number", alias="telephoneNumber"
    )
    mobile: Optional[str] = Field(None, description="Mobile number")
    ou: Optional[str] = Field(None, description="Organizational unit")
    object_class: List[str] = Field(
        default=["inetOrgPerson", "organizationalPerson", "person", "top"],
        description="LDAP object classes",
        alias="objectClass",
    )

    class Config:
        allow_population_by_field_name = True


class GroupOfNames(BaseModel):
    """LDAP groupOfNames entity model."""

    cn: str = Field(..., description="Group common name")
    description: Optional[str] = Field(None, description="Group description")
    member: List[str] = Field(
        default_factory=list, description="List of member DNs"
    )
    object_class: List[str] = Field(
        default=["groupOfNames", "top"],
        description="LDAP object classes",
        alias="objectClass",
    )

    class Config:
        allow_population_by_field_name = True


class OrganizationalUnit(BaseModel):
    """LDAP organizationalUnit entity model."""

    ou: str = Field(..., description="Organizational unit name")
    description: Optional[str] = Field(None, description="OU description")
    object_class: List[str] = Field(
        default=["organizationalUnit", "top"],
        description="LDAP object classes",
        alias="objectClass",
    )

    class Config:
        allow_population_by_field_name = True
