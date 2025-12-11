"""Models for LDIF generation API."""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationJob(BaseModel):
    """Generation job model."""
    job_id: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_records: int = 0
    output_records: int = 0
    error_message: Optional[str] = None
    progress_percentage: int = 0


class GenerationRequest(BaseModel):
    """Request model for LDIF generation."""
    data: List[Dict[str, Any]] = Field(..., description="List of records to convert to LDIF")
    schema_name: str = Field(..., description="Name of schema to use for validation")
    base_dn: str = Field(default="", description="Base DN for LDIF entries")
    object_classes: List[str] = Field(default=["inetOrgPerson"], description="LDAP object classes")
    format: str = Field(default="ldif", description="Output format (ldif or json)")


class GenerationResponse(BaseModel):
    """Response model for LDIF generation."""
    job_id: str
    status: JobStatus
    message: str
    output: Optional[str] = None
    record_count: int = 0
    error_details: Optional[Dict[str, Any]] = None
