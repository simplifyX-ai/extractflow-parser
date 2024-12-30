## Setting up Ollama locally:

1. **Install Ollama** based on your operating system:

   **Linux:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

   **MacOS:**
   ```bash
   brew install ollama
   ```

   **Windows:**
   Download and install from [Ollama Website](https://ollama.com/download/OllamaSetup.exe)

2. **Pull and start** the Ollama server:
   ```bash
   ollama pull llama3.2-vision:11b
   ollama serve
   ```

3. **Verify** server status:
   ```bash
   curl http://localhost:11434/api/version
   ```