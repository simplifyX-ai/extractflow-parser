import pytest
from extractflow_parser import ExtractFlowParserError, UnsupportedFileError


def test_convert_pdf_nonexistent_file(markdown_parser):
    """Test error handling for non-existent PDF files."""
    with pytest.raises(FileNotFoundError) as exc_info:
        markdown_parser.convert_pdf("non-existent.pdf")
    assert "PDF file not found" in str(exc_info.value)


def test_convert_pdf_invalid_file(markdown_parser, tmp_path):
    """Test error handling for invalid file types."""
    # Create a temporary text file
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("test content")

    with pytest.raises(UnsupportedFileError) as exc_info:
        markdown_parser.convert_pdf(invalid_file)
    assert "File is not a PDF" in str(exc_info.value)


def test_calculate_matrix(markdown_parser, pdf_document):
    """Test the matrix calculation for PDF page transformation."""
    page = pdf_document[0]
    matrix = markdown_parser._calculate_matrix(page)
    expected_zoom = markdown_parser.page_config.dpi / 72 * 2
    assert matrix.a == expected_zoom
    assert matrix.d == expected_zoom


def test_convert_pdf_integration(markdown_parser, pdf_path):
    """Integration test for PDF to markdown conversion."""
    converted_pages = markdown_parser.convert_pdf(pdf_path)
    assert isinstance(converted_pages, list)
    assert len(converted_pages) > 0
    assert any(
        isinstance(page, str) and len(page.strip()) > 0 for page in converted_pages
    )


def test_convert_pdf_extractflow_parser_error(markdown_parser, monkeypatch, pdf_path):
    """Test ExtractFlowParserError handling in convert_pdf method."""

    def mock_convert_page(*args, **kwargs):
        raise Exception("Failed to process page")

    monkeypatch.setattr(markdown_parser, "_convert_page", mock_convert_page)

    with pytest.raises(ExtractFlowParserError) as exc_info:
        markdown_parser.convert_pdf(pdf_path)
    assert "Failed to process page" in str(exc_info.value)
