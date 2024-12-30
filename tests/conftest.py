import pytest
from pathlib import Path
import fitz  # PyMuPDF library for PDF handling
from extractflow_parser.parser import PDFPageConfig, ExtractFlowParser


# Fixture providing the path to the test PDF file
@pytest.fixture
def pdf_path():
    return Path("tests/Texas-Holdem-Rules.pdf")


# Fixture configuring PDF page rendering settings
@pytest.fixture
def page_config():
    return PDFPageConfig(
        dpi=400,  # High DPI for better image quality
        color_space="RGB",  # Standard color space for vision models
        include_annotations=True,  # Include PDF annotations in output
        preserve_transparency=False,  # Flatten transparency for consistent rendering
    )


# Fixture initializing the vision-based markdown parser with specific model settings
@pytest.fixture
def markdown_parser(page_config):
    return ExtractFlowParser(
        model_name="llama3.2-vision:11b",
        temperature=0.7,
        top_p=0.7,
        page_config=page_config,
    )


# Fixture handling PDF document lifecycle with proper cleanup
@pytest.fixture
def pdf_document(pdf_path):
    doc = fitz.open(pdf_path)
    yield doc
    doc.close()
