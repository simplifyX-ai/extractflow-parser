class ExtractFlowParserError(Exception):
    """Base exception for ExtractFlow Parser errors."""

    pass


class UnsupportedFileError(ExtractFlowParserError):
    """Raised when an unsupported file type is provided."""

    pass
