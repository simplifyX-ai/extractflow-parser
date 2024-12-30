# Contributing to Extractflow Parse

Thank you for your interest in contributing to Extractflow Parse! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community

## Getting Started

1. **Fork the Repository**
   - Visit the [ExtractFlow Parse repository](https://github.com/simplifyX-ai/extractflow_parser)
   - Click the "Fork" button in the top-right corner
   - Clone your forked repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/extractflow_parser.git
   cd extractflow_parser
   ```

2. **Set Up Development Environment**
   - Install dependencies using uv (recommended):

   For Mac/Linux:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   For Windows:
   ```bash
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   Install project dependencies:
   ```bash
   uv sync --all-extras && source .venv/bin/activate
   ```

## Development Workflow

1. **Create a New Branch**
   ```bash
   # If you are fixing a bug
   git checkout -b bugfix/your-bug-name

   # If you are adding a new feature
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write your code and add tests if applicable
   - Follow PEP 8 guidelines and use type hints where possible
   - Update documentation as needed

3. **Quality Checks**
   Before submitting your changes, run:
   ```bash
   make lint    # Run code linting
   make format  # Format code
   make test    # Run test suite
   ```

## Pull Request Process

1. **Prepare Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to your fork on GitHub and click "New Pull Request"
   - Select your feature branch
   - Fill in the PR template by describing your changes, and referencing related issue.