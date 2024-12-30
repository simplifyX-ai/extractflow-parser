import fitz  # PyMuPDF library for PDF processing
from pathlib import Path
from typing import Optional, List, Union, Any
from tqdm import tqdm
import base64
from pydantic import BaseModel
from .llm import LLM


class PDFPageConfig(BaseModel):
    """Configuration settings for PDF page conversion."""

    dpi: int = 400  # Resolution for PDF to image conversion
    color_space: str = "RGB"  # Color mode for image output
    include_annotations: bool = True  # Include PDF annotations in conversion
    preserve_transparency: bool = False  # Control alpha channel in output


class UnsupportedFileError(BaseException):
    """Custom exception for handling unsupported file errors."""

    pass


class ExtractFlowParserError(BaseException):
    """Custom exception for handling Markdown Parser errors."""

    pass


class ExtractFlowParser:
    """Convert PDF pages to base64-encoded images and then extract text from the images in markdown format."""

    def __init__(
        self,
        page_config: Optional[PDFPageConfig] = None,
        model_name: str = "llama3.2-vision:11b",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        top_p: float = 0.3,
        extraction_complexity: bool = False,
        openai_compatible: bool = False,
        base_url: Optional[str] = None,  # Optional: Only used for OpenAI models
        **kwargs: Any,
    ):
        """Initialize parser with PDFPageConfig and LLM configuration."""
        self.page_config = page_config or PDFPageConfig()

        llm_kwargs = {
            "model_name": model_name,
            "temperature": temperature,
            "top_p": top_p,
            "api_key": api_key,
            "complexity": extraction_complexity,
            **kwargs,
        }

        # Add base_url only if it's an OpenAI model
        if base_url:
            llm_kwargs["base_url"] = base_url
        
        if openai_compatible:
            llm_kwargs["openai_compatible"] = openai_compatible

        self.llm = LLM(**llm_kwargs)

    def _calculate_matrix(self, page: fitz.Page) -> fitz.Matrix:
        """Calculate transformation matrix for page conversion."""
        # Calculate zoom factor based on target DPI
        zoom = self.page_config.dpi / 72  # 72 is the base PDF DPI
        # Double zoom for better quality and text recognition
        matrix = fitz.Matrix(zoom * 2, zoom * 2)

        # Handle page rotation if present
        if page.rotation != 0:
            matrix.prerotate(page.rotation)

        return matrix

    def _convert_page(self, page: fitz.Page, page_number: int) -> str:
        """Convert a single PDF page into base64-encoded PNG and extract markdown formatted text."""
        try:
            matrix = self._calculate_matrix(page)

            # Create high-quality image from PDF page
            pix = page.get_pixmap(
                matrix=matrix,
                alpha=self.page_config.preserve_transparency,
                colorspace=self.page_config.color_space,
                annots=self.page_config.include_annotations,
            )

            # Convert image to base64 for LLM processing
            base64_encoded = base64.b64encode(pix.tobytes("png")).decode("utf-8")

        except Exception as e:
            raise ExtractFlowParserError(
                f"Failed to convert page {page_number + 1} to base64-encoded PNG: {str(e)}"
            )
        finally:
            # Clean up pixmap to free memory
            if pix is not None:
                pix = None

        return self.llm.generate_markdown(base64_encoded)

    def convert_pdf(self, pdf_path: Union[str, Path]) -> List[str]:
        """Convert all pages in the given PDF file to markdown text."""
        pdf_path = Path(pdf_path)
        converted_pages = []

        if not pdf_path.exists() or not pdf_path.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise UnsupportedFileError(f"File is not a PDF: {pdf_path}")

        try:
            # Process PDF document page by page
            with fitz.open(pdf_path) as pdf_document:
                total_pages = pdf_document.page_count

                with tqdm(
                    total=total_pages,
                    desc="Converting pages in PDF file into markdown format",
                ) as pbar:
                    for page_number in range(total_pages):
                        text = self._convert_page(
                            pdf_document[page_number], page_number
                        )

                        converted_pages.append(text)
                        pbar.update(1)

            return converted_pages

        except Exception as e:
            raise ExtractFlowParserError(
                f"Failed to convert PDF file into markdown content: {str(e)}"
            )
