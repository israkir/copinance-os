# Installation

Get Copinance OS installed and ready to use.

## Prerequisites

- Python 3.11 or higher
- `make` (optional, but recommended)

## Quick Installation

**Recommended (with make):**
```bash
git clone https://github.com/copinance/copinance-os.git
cd copinance-os
make setup
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks

**Manual installation:**
```bash
git clone https://github.com/copinance/copinance-os.git
cd copinance-os
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Verify Installation

```bash
copinance version
# or
python -m copinanceos.cli version
```

Expected output:
```
Copinance OS v0.1.0
```

## Optional Dependencies

**For documentation:**
```bash
pip install -e ".[docs]"
```

**For local LLM support (Ollama):**
```bash
pip install -e ".[ollama]"
```

## No Installation Needed

You can run the CLI directly without installing:
```bash
python -m copinanceos.cli version
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first research
- [Configuration](../user-guide/configuration.md) - Set up API keys
