# Copinance OS Documentation

Welcome to Copinance OS - an open-source stock research platform and framework.

## What is Copinance OS?

Copinance OS is a Python library that helps you perform comprehensive stock research with:
- **Dual workflow support** (static pipelines and AI-powered agentic workflows)
- **Adaptive presentation** based on financial literacy level
- **Extensible architecture** for custom data providers and analyzers

## Quick Navigation

### 🚀 Getting Started
- [Installation](getting-started/installation.md) - Get up and running
- [Quick Start](getting-started/quickstart.md) - Your first research in 5 minutes

### 👤 User Guide
- [CLI Reference](user-guide/cli.md) - Complete command reference
- [Workflows](user-guide/workflows.md) - Static and agentic workflows
- [Configuration](user-guide/configuration.md) - Setting up API keys and options

### 🔧 Developer Guide
- [Architecture](developer-guide/architecture.md) - System design and patterns
- [Extending](developer-guide/extending.md) - Adding custom data providers
- [Testing](developer-guide/testing.md) - Test structure and guidelines

### 📚 API Reference
- [Data Providers](api-reference/data-providers.md) - Data provider interfaces

## Key Concepts

### Research Profiles
Research profiles provide context for research execution (financial literacy level, preferences). This is **NOT** user management - your app handles users, we handle research context.

### Workflow Types
- **Static**: Predefined analysis pipeline with consistent steps
- **Agentic**: AI-powered dynamic analysis that adapts to questions

## Need Help?

- 📖 Check the [User Guide](user-guide/cli.md) for common tasks
- 🐛 Report issues on [GitHub](https://github.com/copinance/copinance-os/issues)
- 💬 Join discussions in the repository
