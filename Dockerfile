FROM python:3.13-slim

# Accept build argument
ARG MODEL_NAME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama only for Ollama-based models
RUN case "$MODEL_NAME" in \
    "llama3.2-vision:11b"|"llama3.2-vision:70b"|"llava:13b"|"llava:34b") \
    curl -fsSL https://ollama.com/install.sh | sh \
    ;; \
    esac

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install extractflow_parser with all optional dependencies
RUN pip install --no-cache-dir 'extractflow_parser[all]'

# Create a startup script
RUN echo '#!/bin/bash\n\
case "$MODEL_NAME" in\n\
    "llama3.2-vision:11b"|"llama3.2-vision:70b"|"llava:13b"|"llava:34b")\n\
        ollama serve > /var/log/ollama.log 2>&1 &\n\
        sleep 10\n\
        ollama pull $MODEL_NAME\n\
        ;;\n\
esac\n\
exec "$@"' > /start.sh && chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
CMD ["tail", "-f", "/dev/null"] 