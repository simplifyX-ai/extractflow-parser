# ExtractFlow Parse

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)


## 🚀 Getting Started

### Prerequisites

- 🐍 Python >= 3.9
- 🖥️ Ollama (if you want to use local models)
- 🤖 API Key for OpenAI (OpenAI compatible models) or Google Gemini (if you want to use OpenAI or Google Gemini)

## Models Support

ExtractFlow supports various vision language models from different providers:

### OpenAI Compatible Models
- You can use any model that is compatible with OpenAI API.
- By passing `openai_compatible=True`, and `base_url` to the parser, the parser will use the OpenAI API to process the image.

### Ollama Models
- `llama3.2-vision:11b`
- `llama3.2-vision:70b`
- `llava:13b`
- `llava:34b`

### OpenAI Models
- `gpt-4o`
- `gpt-4o-mini`

### Gemini Models
- `gemini-1.5-flash`
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro`


### Installation

Install the package using pip (Recommended):

```bash
pip install extractflow_parser
```

Install the optional dependencies for OpenAI or Gemini:
```bash
pip install 'extractflow_parser[openai]'
```

```bash
pip install 'extractflow_parser[gemini]'
```

### The easiest way to get started is by exploring the [examples](examples) folder for additional sample use cases.

[Azure LLama Vision](examples/azure_llama_vision_openai_compatible_demo.ipynb)
[QWEN2-VL](examples/azure_qwen2-vl_openai_compatible_demo.ipynb)
[OpenAI](examples/openai_demo.ipynb)
[Gemini](examples/gemini_demo.ipynb)
[Ollama](examples/ollama_demo.ipynb)


### Setting up Ollama (Optional)
See [examples/ollama_setup.md](examples/ollama_setup.md) on how to setup Ollama locally.

## ⌛️ Usage

### Basic Example Usage

```python
from extractflow_parser import ExtractFlowParser

# Initialize parser
parser = ExtractFlowParser(
    openai_compatible=True,
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="your_api_key",
    model_name="accounts/fireworks/models/qwen2-vl-72b-instruct",
    temperature=0.2,
    top_p=0.3,
    extraction_complexity=True # Set to True for more detailed extraction
)

# Convert PDF to markdown
pdf_path = "path/to/your/document.pdf"
markdown_pages = parser.convert_pdf(pdf_path)

# Process results
for i, page_content in enumerate(markdown_pages):
    print(f"\n--- Page {i+1} ---\n{page_content}")
```

### PDF Page Configuration

```python
from extractflow_parser import ExtractFlowParser, PDFPageConfig

# Configure PDF processing settings
page_config = PDFPageConfig(
    dpi=400,
    color_space="RGB",
    include_annotations=True,
    preserve_transparency=False
)

# Initialize parser with custom page config
parser = ExtractFlowParser(
    model_name="llama3.2-vision:11b",
    temperature=0.7,
    top_p=0.4,
    extraction_complexity=False,
    page_config=page_config
)

# Convert PDF to markdown
pdf_path = "path/to/your/document.pdf"
markdown_pages = parser.convert_pdf(pdf_path)
```

### OpenAI or Gemini Model Usage

```python
from extractflow_parser import ExtractFlowParser

# Initialize parser with OpenAI model
parser = ExtractFlowParser(
    model_name="gpt-4o",
    api_key="your-openai-api-key", # Get the OpenAI API key from https://platform.openai.com/api-keys
    temperature=0.7,
    top_p=0.4,
    extraction_complexity=True # Set to True for more detailed extraction
)

# Initialize parser with Google Gemini model
parser = ExtractFlowParser(
    model_name="gemini-1.5-flash",
    api_key="your-gemini-api-key", # Get the Gemini API key from https://aistudio.google.com/app/apikey
    temperature=0.7,
    top_p=0.4,
    extraction_complexity=True # Set to True for more detailed extraction
)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
