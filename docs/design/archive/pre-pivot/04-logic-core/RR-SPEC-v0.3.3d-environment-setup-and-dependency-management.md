# Environment Setup & Dependency Management

> **v0.3.3d Baseline Agent — Logic Core**
> Defines environment configuration, dependency management, and security practices for running the DocumentationAgent. Covers local development, testing, and CI/CD deployment.

## Objective

Create a complete environment setup that:
- Secures API keys and credentials
- Manages Python dependencies with pinned versions
- Provides reproducible local development setup
- Enables CI/CD testing without real API keys
- Supports testing across OpenAI, Anthropic, and Ollama providers
- Documents fallback strategies when APIs are unavailable

## Scope Boundaries

**INCLUDES:**
- Environment variable strategy and .env management
- API key security and handling
- requirements.txt with pinned versions
- Virtual environment setup
- .env.example template
- CI/CD environment configuration (GitHub Actions)
- Mock strategy for testing without real APIs
- Setup instructions for all platforms (Linux, macOS, Windows)

**EXCLUDES:**
- Application deployment infrastructure
- Database configuration
- User authentication systems
- Secret management systems (AWS Secrets Manager, etc.)
- Docker or container setup

---

## Dependency Diagram

```
PROJECT ROOT/
├── .env (local, git-ignored)
├── .env.example (template, committed)
├── requirements.txt (pinned versions)
├── pyproject.toml (optional, project metadata)
├── python/ (or src/)
│   └── agent.py (imports from requirements)
├── tests/
│   └── test_agent.py (uses mocks, doesn't need real keys)
├── .github/
│   └── workflows/
│       └── test.yml (CI/CD, uses env secrets)
└── README.md (setup instructions)
```

---

## 1. Environment Variable Strategy

### Fallback Chain for Configuration

```python
def get_api_key(provider: str) -> str:
    """
    Get API key using fallback chain:
    1. Function parameter (explicit)
    2. Environment variable
    3. .env file (if loaded)
    4. Config file in home directory
    5. Raise error
    """

    import os
    from pathlib import Path
    from dotenv import load_dotenv

    # Determine env var name based on provider
    env_var_names = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "ollama": "OLLAMA_BASE_URL"  # Ollama uses URL, not API key
    }

    env_var = env_var_names.get(provider)
    if not env_var:
        raise ValueError(f"Unknown provider: {provider}")

    # Step 1: Check environment variables
    if env_var in os.environ:
        return os.environ[env_var]

    # Step 2: Load .env file if not already loaded
    if not os.environ.get("_DOTENV_LOADED"):
        dotenv_path = Path.cwd() / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            os.environ["_DOTENV_LOADED"] = "true"

            # Retry after loading
            if env_var in os.environ:
                return os.environ[env_var]

    # Step 3: Check config file in home directory
    config_path = Path.home() / ".docstratum" / "config.env"
    if config_path.exists():
        from dotenv import dotenv_values
        config = dotenv_values(config_path)
        if env_var in config:
            return config[env_var]

    # Step 4: Not found
    raise ValueError(
        f"{env_var} not found. Set as environment variable, "
        f"add to .env file, or add to ~/.docstratum/config.env"
    )
```

### Environment Variable Precedence

| Priority | Source | Example |
|----------|--------|---------|
| **1** | Function parameter | `DocumentationAgent(..., api_key="sk-...")` |
| **2** | Environment variable | `export OPENAI_API_KEY=sk-...` |
| **3** | .env file (local) | `.env` in project root |
| **4** | Config file | `~/.docstratum/config.env` |
| **5** | Error | Raise ValueError with helpful message |

---

## 2. API Key Security Practices

### Never Log Keys

```python
def log_safe(message: str, value: str = None) -> str:
    """
    Log message with value, but mask sensitive keys.

    Example:
        log_safe("API Key", "sk-1234567890abc")
        → "API Key: sk-****67890abc"
    """

    if not value:
        return message

    # Don't log anything that looks like a key
    if any(prefix in str(value)[:10] for prefix in ["sk-", "sk_", "api_", "token_"]):
        masked = value[:6] + "****" + value[-8:]
        return f"{message}: {masked}"

    return f"{message}: {value}"

def safe_error_message(error: Exception) -> str:
    """Extract error message without exposing API key"""
    msg = str(error)

    # Remove common key patterns
    import re
    msg = re.sub(r'sk-[a-zA-Z0-9]{45}', 'sk-****', msg)
    msg = re.sub(r'sk_[a-zA-Z0-9]{45}', 'sk_****', msg)
    msg = re.sub(r'Bearer [a-zA-Z0-9]*', 'Bearer ****', msg)

    return msg

# EXAMPLE: Safe logging
try:
    api_key = get_api_key("openai")
    # NEVER: logger.info(f"Using key: {api_key}")
    # DO THIS: logger.info(log_safe("Using OpenAI key", api_key))
except Exception as e:
    # NEVER: logger.error(f"Failed: {e}")  # Might leak key in error
    # DO THIS:
    logger.error(f"Failed: {safe_error_message(e)}")
```

### .env Security

```
# .gitignore (ensure .env is not committed)
.env
.env.local
.env.*.local
config/secrets/
~/.docstratum/

# DO commit
.env.example
.env.template
```

### File Permissions

```bash
# When creating .env file, restrict permissions
touch .env
chmod 600 .env  # Only owner can read/write

# Same for config directory
mkdir -p ~/.docstratum
chmod 700 ~/.docstratum
touch ~/.docstratum/config.env
chmod 600 ~/.docstratum/config.env
```

---

## 3. Dependency List & Pinned Versions

### requirements.txt

```
# Core LangChain and LLM integrations
langchain==0.1.14
langchain-core==0.1.42
langchain-openai==0.1.15
langchain-anthropic==0.1.19
langchain-community==0.0.30

# Supporting libraries
python-dotenv==1.0.0  # For .env file loading
pydantic==2.5.2       # For data validation
requests==2.31.0      # HTTP library (LangChain dependency)
aiohttp==3.9.1        # Async HTTP (LangChain dependency)

# Testing and development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-timeout==2.2.0
responses==0.24.1     # Mock HTTP responses

# Code quality
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.2

# Optional: for better error messages
rich==13.7.0
```

### Why These Versions?

```
langchain==0.1.14
├─ Reason: Stable version with good provider support
├─ Don't use: 0.2.x (major refactoring, breaking changes)
├─ Check: https://github.com/langchain-ai/langchain/releases

langchain-openai==0.1.15
├─ Reason: Matches langchain version, stable API
├─ Latest at: 0.1.x series
└─ Note: Must match langchain major version (0.1.x with 0.1.x)

python-dotenv==1.0.0
├─ Reason: Latest stable, widely used, simple API
└─ Usage: from dotenv import load_dotenv; load_dotenv()

pytest==7.4.3
├─ Reason: Latest stable, good plugin ecosystem
└─ Usage: pytest tests/ -v
```

---

## 4. Virtual Environment Setup

### Linux / macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) prefix)
which python
# Output: /path/to/project/venv/bin/python

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import langchain; print(langchain.__version__)"
```

### Windows

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) prefix in prompt)
where python
# Output: X:\path\to\project\venv\Scripts\python.exe

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import langchain; print(langchain.__version__)"
```

### Deactivation

```bash
# Either platform
deactivate
```

---

## 5. .env.example Template

```bash
# .env.example
# Template for environment configuration
# Copy to .env and fill in actual values
# NEVER commit .env file with real credentials

# OpenAI Configuration
# Get key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# Anthropic Configuration
# Get key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Ollama Configuration
# If using local Ollama instead of API
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Optional: Default provider (openai, anthropic, or ollama)
DEFAULT_PROVIDER=openai

# Optional: Default model
DEFAULT_MODEL=gpt-4o-mini

# Optional: API timeout in seconds
API_TIMEOUT_SEC=30

# Optional: Disable API calls for testing (use mocks)
USE_MOCK_API=false
```

### Setup Instructions

```bash
# 1. Copy template to .env
cp .env.example .env

# 2. Edit .env and add real API keys
nano .env  # or vim, code, etc.

# 3. Verify .env is in .gitignore
cat .gitignore | grep "\.env"
# Should output: .env

# 4. Test that keys are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Keys loaded:', 'OPENAI_API_KEY' in os.environ)"
```

---

## 6. CI/CD Environment (GitHub Actions)

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests with coverage
      env:
        # Secrets from GitHub Actions
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        USE_MOCK_API: false
      run: |
        pytest tests/ -v --cov=agent --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Setting Up GitHub Secrets

```
1. Go to: https://github.com/YOUR_ORG/docstratum/settings/secrets/actions
2. Click "New repository secret"
3. Add secrets:
   - Name: OPENAI_API_KEY
     Value: sk-... (from OpenAI)
   - Name: ANTHROPIC_API_KEY
     Value: sk-ant-... (from Anthropic)
4. Secrets are masked in logs automatically
5. Available in CI as: ${{ secrets.OPENAI_API_KEY }}
```

---

## 7. Mock Strategy for Testing

### Testing Without Real API Calls

```python
# tests/test_agent_with_mocks.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent import DocumentationAgent, AgentResponse

class TestDocumentationAgentMocked:
    """Test agent without making real API calls"""

    @patch('langchain_openai.ChatOpenAI')
    def test_invoke_with_mock_openai(self, mock_chat):
        """Test invoke() with mocked OpenAI"""

        # Setup mock response
        mock_response = Mock()
        mock_response.content = "REST API is an interface..."
        mock_response.response_metadata = {
            "usage": {
                "prompt_tokens": 187,
                "completion_tokens": 45
            }
        }
        mock_chat.return_value.invoke.return_value = mock_response

        # Create agent with mock
        with patch('agent.ChatOpenAI', return_value=mock_chat.return_value):
            agent = DocumentationAgent(
                system_prompt="You are helpful.",
                model="gpt-4o-mini",
                api_key="test-key"
            )

            # Invoke and verify
            response = agent.invoke("What is REST API?")

            assert response.is_success()
            assert "REST API" in response.response
            assert response.total_tokens == 232

    @patch('langchain_anthropic.ChatAnthropic')
    def test_invoke_with_mock_anthropic(self, mock_chat):
        """Test invoke() with mocked Anthropic"""

        mock_response = Mock()
        mock_response.content = "A REST API is..."
        mock_response.response_metadata = {
            "usage": {
                "input_tokens": 200,
                "output_tokens": 50
            }
        }
        mock_chat.return_value.invoke.return_value = mock_response

        with patch('agent.ChatAnthropic', return_value=mock_chat.return_value):
            agent = DocumentationAgent(
                system_prompt="You are helpful.",
                model="claude-3-5-sonnet-20241022",
                api_key="test-key"
            )

            response = agent.invoke("What is REST API?")

            assert response.is_success()
            assert response.total_tokens == 250

    @patch('agent.ChatOpenAI')
    def test_invoke_with_timeout_error(self, mock_chat):
        """Test error handling with mocked timeout"""

        mock_chat.return_value.invoke.side_effect = TimeoutError("API timeout")

        with patch('agent.ChatOpenAI', return_value=mock_chat.return_value):
            agent = DocumentationAgent(
                system_prompt="You are helpful.",
                api_key="test-key"
            )

            response = agent.invoke("What is REST API?")

            assert response.is_error()
            assert "timeout" in response.error.lower()
            assert response.response == ""
```

### VCR.py for Recording/Replaying API Calls

```python
# tests/test_agent_with_vcr.py
import pytest
from vcr_py import VCR
from agent import DocumentationAgent

# Record API calls on first run, replay on subsequent runs
my_vcr = VCR(
    cassette_library_dir='tests/fixtures/cassettes',
    record_mode='once',  # Record on first run, replay after
)

class TestWithVCR:

    @my_vcr.use_cassette('test_openai_response.yaml')
    def test_openai_integration(self):
        """Test real API (recorded once, then mocked)"""
        agent = DocumentationAgent(
            system_prompt="You are helpful.",
            api_key="real-key"  # Uses env var if available
        )

        response = agent.invoke("What is REST API?")

        # First run: calls real API, saves to cassette
        # Subsequent runs: uses recorded response from cassette
        assert response.is_success()

# Cassette files (version controlled, can share without API keys)
# tests/fixtures/cassettes/test_openai_response.yaml
```

---

## 8. Setup Instructions for End Users

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/anthropic/docstratum.git
cd docstratum

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env and add your API keys

# 5. Test installation
python -c "from agent import DocumentationAgent; print('Success!')"

# 6. Run tests
pytest tests/ -v
```

### Troubleshooting

```bash
# Issue: "python3: command not found" (Windows)
# Solution: Use "python" instead of "python3"
python -m venv venv

# Issue: "Permission denied" activation script (Linux/macOS)
# Solution: Make activation script executable
chmod +x venv/bin/activate

# Issue: "ModuleNotFoundError: No module named 'dotenv'"
# Solution: Reinstall requirements
pip install --force-reinstall -r requirements.txt

# Issue: "API key not found"
# Solution: Verify .env file exists and contains key
cat .env | grep OPENAI_API_KEY

# Issue: Tests fail with "Rate limit exceeded"
# Solution: Use USE_MOCK_API=true in .env for local testing
```

---

## Deliverables

1. **requirements.txt** with all pinned versions
2. **.env.example** template
3. **Virtual environment setup instructions** (all platforms)
4. **API key security guidelines**
5. **GitHub Actions workflow** (.github/workflows/test.yml)
6. **Mock testing examples** with unittest.mock and VCR
7. **Setup instructions** (Quick Start + Troubleshooting)
8. **Fallback chain implementation** for configuration

---

## Acceptance Criteria

- [ ] requirements.txt includes all dependencies with pinned versions
- [ ] .env.example contains all needed variables
- [ ] .env is in .gitignore (never committed)
- [ ] Virtual environment setup works on Linux, macOS, and Windows
- [ ] API keys are never logged or printed
- [ ] Tests can run without real API keys (using mocks)
- [ ] GitHub Actions workflow passes with secrets
- [ ] Mock strategy is documented and working
- [ ] Setup takes less than 10 minutes
- [ ] Error messages don't expose API keys

---

## Next Step

**v0.3.4a — Context Injection & System Prompt Assembly** will build on this foundation to create the DocStratum-enhanced agent that injects rich context into the system prompt.
