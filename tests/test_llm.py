import pytest
from unittest.mock import patch, MagicMock
import json
import base64
from extractflow_parser.llm import LLM, UnsupportedModelError, LLMError


@pytest.fixture
def sample_base64_image():
    return base64.b64encode(b"test_image").decode("utf-8")


@pytest.fixture
def mock_structured_response():
    return {
        "message": {
            "content": json.dumps(
                {
                    "text_detected": "Yes",
                    "tables_detected": "No",
                    "extracted_text": "Test content",
                    "confidence_score_text": 0.9,
                }
            )
        }
    }


@pytest.fixture
def mock_markdown_response():
    return {"message": {"content": "# Test Header\n\nThis is test content."}}


def test_unsupported_model():
    """Test error handling for unsupported models."""
    with pytest.raises(UnsupportedModelError) as exc_info:
        LLM(
            model_name="unsupported-model",
            temperature=0.7,
            top_p=0.7,
            api_key=None,
            complexity=True,
        )
    assert "is not supported" in str(exc_info.value)


@patch("ollama.chat")
def test_ollama_generate_markdown(
    mock_chat, sample_base64_image, mock_structured_response, mock_markdown_response
):
    """Test markdown generation using Ollama."""
    mock_chat.side_effect = [mock_structured_response, mock_markdown_response]

    llm = LLM(
        model_name="llama3.2-vision:11b",
        temperature=0.7,
        top_p=0.7,
        api_key=None,
        complexity=True,
    )
    result = llm.generate_markdown(sample_base64_image)

    assert isinstance(result, str)
    assert "Test Header" in result
    assert mock_chat.call_count == 2


@patch("openai.OpenAI")
def test_openai_generate_markdown(MockOpenAI, sample_base64_image):
    """Test markdown generation using OpenAI."""
    mock_client = MagicMock()
    MockOpenAI.return_value = mock_client

    # Mock structured analysis response
    mock_client.beta.chat.completions.parse.return_value.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "text_detected": "Yes",
                        "tables_detected": "No",
                        "extracted_text": "Test content",
                        "confidence_score_text": 0.9,
                    }
                )
            )
        )
    ]

    # Mock markdown conversion response
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="# Test Header\n\nThis is test content."))
    ]

    llm = LLM(
        model_name="gpt-4o",
        api_key="test-key",
        temperature=0.7,
        top_p=0.7,
        complexity=True,
    )
    result = llm.generate_markdown(sample_base64_image)

    assert isinstance(result, str)
    assert "Test Header" in result
    assert mock_client.beta.chat.completions.parse.called
    assert mock_client.chat.completions.create.called


@patch("google.generativeai.GenerativeModel")
def test_gemini_generate_markdown(MockGenerativeModel, sample_base64_image):
    """Test markdown generation using Gemini."""
    mock_client = MagicMock()
    MockGenerativeModel.return_value = mock_client

    # Mock responses for both structured analysis and markdown generation
    mock_client.generate_content.side_effect = [
        MagicMock(
            text=json.dumps(
                {
                    "text_detected": "Yes",
                    "tables_detected": "No",
                    "extracted_text": "Test content",
                    "confidence_score_text": 0.9,
                }
            )
        ),
        MagicMock(text="# Test Header\n\nThis is test content."),
    ]

    llm = LLM(
        model_name="gemini-1.5-pro",
        api_key="test-key",
        temperature=0.7,
        top_p=0.7,
        complexity=True,
    )
    result = llm.generate_markdown(sample_base64_image)

    assert isinstance(result, str)
    assert "Test Header" in result
    assert mock_client.generate_content.call_count == 2


@patch("ollama.chat")
def test_ollama_llm_error(mock_chat, sample_base64_image):
    """Test LLMError handling for Ollama."""
    mock_chat.side_effect = Exception("Ollama processing failed")

    llm = LLM(
        model_name="llama3.2-vision:11b",
        temperature=0.7,
        top_p=0.7,
        api_key=None,
        complexity=True,
    )
    with pytest.raises(LLMError) as exc_info:
        llm.generate_markdown(sample_base64_image)
    assert "Ollama Model processing failed" in str(exc_info.value)


@patch("openai.OpenAI")
def test_openai_llm_error(MockOpenAI, sample_base64_image):
    """Test LLMError handling for OpenAI."""
    mock_client = MagicMock()
    MockOpenAI.return_value = mock_client

    # Mock structured analysis response
    mock_client.beta.chat.completions.parse.return_value.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "text_detected": "Yes",
                        "tables_detected": "No",
                        "extracted_text": "Test content",
                        "confidence_score_text": 0.9,
                    }
                )
            )
        )
    ]

    # Mock API error for markdown generation
    mock_client.chat.completions.create.side_effect = Exception("OpenAI API error")

    llm = LLM(
        model_name="gpt-4o",
        api_key="test-key",
        temperature=0.7,
        top_p=0.7,
        complexity=True,
    )
    with pytest.raises(LLMError) as exc_info:
        llm.generate_markdown(sample_base64_image)
    assert "OpenAI Model processing failed" in str(exc_info.value)


@patch("google.generativeai.GenerativeModel")
def test_gemini_llm_error(MockGenerativeModel, sample_base64_image):
    """Test LLMError handling for Gemini."""
    mock_client = MagicMock()
    MockGenerativeModel.return_value = mock_client

    # Mock API error
    mock_client.generate_content.side_effect = Exception("Gemini API error")

    llm = LLM(
        model_name="gemini-1.5-pro",
        api_key="test-key",
        temperature=0.7,
        top_p=0.7,
        complexity=True,
    )
    with pytest.raises(LLMError) as exc_info:
        llm.generate_markdown(sample_base64_image)
    assert "Gemini Model processing failed" in str(exc_info.value)
