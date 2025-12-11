"""Unified data parser service."""
from typing import Dict, List, Any
from app.models.data_models import (
    DataParserConfig,
    ParsingResult,
    DataFormat,
)
from .csv_parser import parse_csv_string, parse_csv_file
from .json_parser import parse_json_string, parse_json_file


class DataParserService:
    """Unified service for parsing CSV and JSON data."""

    def __init__(self, config: DataParserConfig):
        """
        Initialize parser service with configuration.
        
        Args:
            config: Parser configuration
        """
        self.config = config

    def parse_content(self, content: str) -> ParsingResult:
        """
        Parse data from string content.
        
        Args:
            content: Data content as string
            
        Returns:
            ParsingResult with parsed data
        """
        if self.config.format == DataFormat.CSV:
            return parse_csv_string(content, self.config.schema)
        elif self.config.format == DataFormat.JSON:
            return parse_json_string(content, self.config.schema)
        else:
            raise ValueError(f"Unsupported data format: {self.config.format}")

    async def parse_file(self, filepath: str) -> ParsingResult:
        """
        Parse data from a file.
        
        Args:
            filepath: Path to data file
            
        Returns:
            ParsingResult with parsed data
        """
        if self.config.format == DataFormat.CSV:
            return await parse_csv_file(filepath, self.config.schema)
        elif self.config.format == DataFormat.JSON:
            return await parse_json_file(filepath, self.config.schema)
        else:
            raise ValueError(f"Unsupported data format: {self.config.format}")
