"""Unified parser service for CSV and JSON data."""
from typing import Dict, List, Any, Optional
from app.models.data_models import DataParserConfig, ParsingResult, DataFormat
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.json_parser import JSONParser


class DataParserService:
    """Unified service for parsing CSV and JSON data."""
    
    def __init__(self, config: DataParserConfig):
        """Initialize parser service with configuration."""
        self.config = config
        self.parser = self._get_parser()
    
    def _get_parser(self):
        """Get appropriate parser based on configuration."""
        if self.config.format == DataFormat.CSV:
            return CSVParser(self.config)
        elif self.config.format == DataFormat.JSON:
            return JSONParser(self.config)
        else:
            raise ValueError(f"Unsupported data format: {self.config.format}")
    
    def parse_content(self, content: str) -> ParsingResult:
        """Parse data from string content."""
        if self.config.format == DataFormat.CSV:
            return self.parser.parse_string(content)
        elif self.config.format == DataFormat.JSON:
            return self.parser.parse_string(content)
        else:
            raise ValueError(f"Unsupported data format: {self.config.format}")
    
    def parse_file(self, file_path: str) -> ParsingResult:
        """Parse data from file."""
        return self.parser.parse_file(file_path)
    
    def parse_files(self, file_paths: List[str]) -> List[ParsingResult]:
        """Parse multiple files."""
        return self.parser.parse_files(file_paths)
    
    def parse_directory(self, directory_path: str, file_extension: Optional[str] = None) -> List[ParsingResult]:
        """Parse all files in a directory with specified extension."""
        import os
        
        results = []
        file_paths = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                if file_extension is None or filename.endswith(file_extension):
                    file_paths.append(file_path)
        
        if file_paths:
            results = self.parse_files(file_paths)
        
        return results


# Convenience functions for common use cases
def parse_csv_string(csv_content: str, schema: Dict[str, Any], validate: bool = True) -> ParsingResult:
    """Parse CSV content from string with given schema."""
    config = DataParserConfig(
        format=DataFormat.CSV,
        schema=schema,
        validate_on_parse=validate
    )
    service = DataParserService(config)
    return service.parse_content(csv_content)


def parse_csv_file(file_path: str, schema: Dict[str, Any], validate: bool = True) -> ParsingResult:
    """Parse CSV file with given schema."""
    config = DataParserConfig(
        format=DataFormat.CSV,
        schema=schema,
        validate_on_parse=validate
    )
    service = DataParserService(config)
    return service.parse_file(file_path)


def parse_json_string(json_content: str, schema: Dict[str, Any], validate: bool = True) -> ParsingResult:
    """Parse JSON content from string with given schema."""
    config = DataParserConfig(
        format=DataFormat.JSON,
        schema=schema,
        validate_on_parse=validate
    )
    service = DataParserService(config)
    return service.parse_content(json_content)


def parse_json_file(file_path: str, schema: Dict[str, Any], validate: bool = True) -> ParsingResult:
    """Parse JSON file with given schema."""
    config = DataParserConfig(
        format=DataFormat.JSON,
        schema=schema,
        validate_on_parse=validate
    )
    service = DataParserService(config)
    return service.parse_file(file_path)