"""Internal models for data parsing."""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DataFormat(str, Enum):
    """Supported data formats."""
    CSV = "csv"
    JSON = "json"


class ValidationError(BaseModel):
    """Validation error model."""
    field: str
    message: str
    value: Any
    row_number: Optional[int] = None


class SummaryStats(BaseModel):
    """Summary statistics model."""
    total_records: int
    valid_records: int
    invalid_records: int
    validation_errors: List[ValidationError]
    parse_errors: List[str]
    processing_time_ms: float
    data_format: DataFormat


class ParsingResult(BaseModel):
    """Result of parsing operation."""
    data: List[Dict[str, Any]]
    summary: SummaryStats
    errors: List[str]


class DataParserConfig(BaseModel):
    """Configuration for data parser."""
    format: DataFormat
    schema: Dict[str, Any]
    validate_on_parse: bool = True
    max_errors: int = 100
    encoding: str = "utf-8"