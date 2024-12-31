from .parser import (
    ExtractFlowParser,
    PDFPageConfig,
    ExtractFlowParserError,
    UnsupportedFileError,
)
from .llm import LLMError, UnsupportedModelError
from importlib.metadata import version

try:
    __version__ = version("extractflow_parser")
except Exception:
    __version__ = "0.1.0"

__all__ = [
    "ExtractFlowParser",
    "PDFPageConfig",
    "ExtractFlowParserError",
    "UnsupportedFileError",
    "UnsupportedModelError",
    "LLMError",
]
