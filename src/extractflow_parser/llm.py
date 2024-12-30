from typing import Literal, Dict, Any, Union
from pydantic import BaseModel
from jinja2 import Template
import re
from tenacity import retry, stop_after_attempt, wait_exponential

SUPPORTED_MODELS: Dict[str, str] = {
    "llama3.2-vision:11b": "ollama",
    "llama3.2-vision:70b": "ollama",
    "llava:13b": "ollama",
    "llava:34b": "ollama",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gemini-1.5-flash": "gemini",
    "gemini-2.0-flash-exp": "gemini",
    "gemini-1.5-pro": "gemini",
}


class ImageDescription(BaseModel):
    """Model Schema for image description."""

    text_detected: Literal["Yes", "No"]
    tables_detected: Literal["Yes", "No"]
    extracted_text: str
    confidence_score_text: float


class UnsupportedModelError(BaseException):
    """Custom exception for unsupported model names"""

    pass


class LLMError(BaseException):
    """Custom exception for Vision LLM errors"""

    pass


class LLM:
    # Load prompts at class level
    try:
        from importlib.resources import files

        _image_analysis_prompt = (
            files("extractflow_parser").joinpath("img_analysis.prompt").read_text()
        )
        _md_prompt_template = Template(
            files("extractflow_parser").joinpath("md_prompt.j2").read_text()
        )
    except Exception as e:
        raise FileNotFoundError(f"Failed to load prompt files: {str(e)}")

    def __init__(
        self,
        model_name: str,
        temperature: float,
        top_p: float,
        api_key: Union[str, None],
        complexity: bool,
        **kwargs: Any,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.complexity = complexity
        
        # Extract base_url from kwargs if present
        self.base_url = kwargs.pop('base_url', None)
        self.kwargs = kwargs

        self.provider = self._get_provider_name(model_name)

        if self.provider == "ollama":
            import ollama

            try:
                ollama.show(self.model_name)
                self.client = ollama
            except ollama.ResponseError as e:
                if e.status_code == 404:
                    ollama.pull(self.model_name)

                self.client = ollama
            except Exception as e:
                raise LLMError(
                    f"Unable to initialize or download {self.model_name} from Ollama: {str(e)}"
                )

        elif self.provider == "openai":
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI is not installed. Please install it using pip install 'extractflow_parser[openai]'."
                )
            try:
                client_args = {'api_key': api_key}
                if self.base_url:
                    client_args['base_url'] = self.base_url
                self.client = openai.OpenAI(**client_args)
            except openai.OpenAIError as e:
                raise LLMError(f"Unable to initialize OpenAI client: {str(e)}")

        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "Gemini is not installed. Please install it using pip install 'extractflow_parser[gemini]'."
                )

            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model_name=self.model_name)
                self.generation_config = genai.GenerationConfig
            except Exception as e:
                raise LLMError(f"Unable to initialize Gemini client: {str(e)}")

    @classmethod
    def _get_provider_name(cls, model_name: str) -> str:
        """Get the provider name for a given model name."""
        # Check if model starts with "accounts"
        if model_name.startswith("accounts"):
            return "openai"
        
        try:
            return SUPPORTED_MODELS[model_name]
        except KeyError:
            supported_models = ", ".join(
                f"'{model}' from {provider}"
                for model, provider in SUPPORTED_MODELS.items()
            )
            supported_models += "\nAny model starting with 'accounts' will use OpenAI provider"
            raise UnsupportedModelError(
                f"Model '{model_name}' is not supported. "
                f"Supported models are: {supported_models}"
            )

    def generate_markdown(self, base64_encoded: str) -> Any:
        """Generate markdown formatted text from a base64-encoded image using appropriate model provider."""
        if self.complexity:
            if self.provider == "ollama":
                response = self._ollama(
                    base64_encoded, self._image_analysis_prompt, structured=True
                )

            elif self.provider == "openai":
                response = self._openai(
                    base64_encoded, self._image_analysis_prompt, structured=True
                )

            elif self.provider == "gemini":
                response = self._gemini(
                    base64_encoded, self._image_analysis_prompt, structured=True
                )

            json_response = ImageDescription.model_validate_json(response)
            if json_response.text_detected.strip() == "No":
                return ""

            prompt = self._md_prompt_template.render(
                extracted_text=json_response.extracted_text,
                tables_detected=json_response.tables_detected,
                confidence_score_text=float(json_response.confidence_score_text),
            )

        else:
            prompt = self._md_prompt_template.render(
                extracted_text="",
                tables_detected="Yes",
                confidence_score_text=0.0,
            )

        if self.provider == "ollama":
            return self._ollama(base64_encoded, prompt)
        elif self.provider == "openai":
            return self._openai(base64_encoded, prompt)
        elif self.provider == "gemini":
            return self._gemini(base64_encoded, prompt)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def _ollama(
        self, base64_encoded: str, prompt: str, structured: bool = False
    ) -> Any:
        """Process base64-encoded image through Ollama vision models."""
        try:
            response = self.client.chat(
                model=self.model_name,
                format=ImageDescription.model_json_schema() if structured else None,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [base64_encoded],
                    }
                ],
                options={
                    "temperature": 0.0 if structured else self.temperature,
                    "top_p": 0.4 if structured else self.top_p,
                    **self.kwargs,
                },
            )

            return re.sub(
                r"```(?:markdown)?\n(.*?)\n```",
                r"\1",
                response["message"]["content"],
                flags=re.DOTALL,
            )
        except Exception as e:
            raise LLMError(f"Ollama Model processing failed: {str(e)}")

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def _openai(
        self, base64_encoded: str, prompt: str, structured: bool = False
    ) -> Any:
        """Process base64-encoded image through OpenAI vision models."""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_encoded}"
                            },
                        },
                    ],
                }
            ]

            if structured:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    response_format={"type": "json_object"},
                    messages=messages,
                    temperature=0.0,
                    top_p=0.4,
                    **self.kwargs,
                )
                return response.choices[0].message.content

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p,
                **self.kwargs,
            )

            return re.sub(
                r"```(?:markdown)?\n(.*?)\n```",
                r"\1",
                response.choices[0].message.content,
                flags=re.DOTALL,
            )
        except Exception as e:
            raise LLMError(f"OpenAI Model processing failed: {str(e)}")

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def _gemini(
        self, base64_encoded: str, prompt: str, structured: bool = False
    ) -> Any:
        """Process base64-encoded image through Gemini vision models."""
        try:
            response = self.client.generate_content(
                [{"mime_type": "image/png", "data": base64_encoded}, prompt],
                generation_config=self.generation_config(
                    response_mime_type="application/json" if structured else None,
                    response_schema=ImageDescription if structured else None,
                    temperature=0.0 if structured else self.temperature,
                    top_p=0.4 if structured else self.top_p,
                    **self.kwargs,
                ),
            )

            return re.sub(
                r"```(?:markdown)?\n(.*?)\n```", r"\1", response.text, flags=re.DOTALL
            )
        except Exception as e:
            raise LLMError(f"Gemini Model processing failed: {str(e)}")
