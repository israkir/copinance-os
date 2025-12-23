# Contributing to Copinance OS

Thank you for your interest in contributing to Copinance OS! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to maintainers@copinance-os.org.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/copinance-os.git`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Setting Up Your Environment

```bash
# Install in development mode with all dependencies
pip install -e ".[dev,docs]"

# Install pre-commit hooks
pre-commit install
```

### Code Style

We follow Python best practices:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **mypy** for type checking
- Type hints required for all functions

Format your code before committing:

```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

### Testing

All code must include tests:

- Unit tests for individual components
- Integration tests for API endpoints
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`

Run tests:

```bash
# All tests
pytest

# With coverage
pytest --cov=copinance

# Specific markers
pytest -m unit
pytest -m integration
```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add sentiment analysis workflow
fix: correct stock search case sensitivity
docs: update API documentation
test: add tests for research orchestrator
refactor: simplify repository interface
```

Prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Architecture Guidelines

### Layer Responsibilities

1. **Domain Layer** (`domain/`)
   - Core business logic
   - No external dependencies
   - Defines ports (interfaces)

2. **Application Layer** (`application/`)
   - Use cases and orchestration
   - Depends only on domain layer
   - Coordinates domain entities

3. **Infrastructure Layer** (`infrastructure/`)
   - External integrations
   - Implements domain ports
   - Configuration and logging
   - Dependency injection containers

4. **CLI Layer** (`cli/`)
   - Command-line interface
   - User-friendly error handling
   - Rich terminal output
   - Depends on application layer

### Best Practices

- **Dependency Inversion**: Depend on abstractions, not implementations
- **Single Responsibility**: Each class/function should have one clear purpose
- **Open/Closed Principle**: Open for extension, closed for modification
- **Interface Segregation**: Prefer small, focused interfaces
- **DRY**: Don't repeat yourself - refactor common code
- **Type Safety**: Use type hints everywhere
- **Testability**: Write testable code with dependency injection

### Adding New Features

When adding features, follow these steps:

1. **Domain Layer**: Define entities and ports if needed
2. **Application Layer**: Implement use cases
3. **Infrastructure Layer**: Implement adapters and repositories
4. **CLI Layer**: Add commands if needed
5. **Tests**: Write comprehensive tests for all layers
6. **Documentation**: Update README and docstrings

## Pull Request Process

1. **Update Tests**: Ensure all tests pass and add new ones
2. **Update Documentation**: Update README, docstrings, and comments
3. **Code Quality**: Run black, ruff, and mypy
4. **Commit Quality**: Use conventional commit messages
5. **PR Description**: Clearly describe changes and rationale
6. **Link Issues**: Reference related issues in PR description

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] Linting passes (`ruff`)
- [ ] Type checking passes (`mypy`)
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (for significant changes)
- [ ] Commit messages follow conventions

## Adding New Workflow Executors

To add a new workflow executor:

1. Create a class implementing `WorkflowExecutor` interface
2. Implement `execute()`, `validate()`, and `get_workflow_type()`
3. Add tests for the executor
4. Register in dependency injection container (`infrastructure/containers/use_cases.py`)

Example:

```python
from copinanceos.domain.ports.workflows import WorkflowExecutor
from copinanceos.domain.models.research import Research

class MyWorkflowExecutor(WorkflowExecutor):
    async def execute(self, research: Research, context: dict) -> dict:
        # Implementation
        pass

    async def validate(self, research: Research) -> bool:
        return research.workflow_type == "my_workflow"

    def get_workflow_type(self) -> str:
        return "my_workflow"
```

## Adding New Repository Implementations

To add a new repository (e.g., PostgreSQL):

1. Create implementation in `infrastructure/repositories/`
2. Implement the appropriate repository interface from `domain/ports/`
3. Add configuration in `infrastructure/config.py`
4. Add tests
5. Update dependency injection

## Questions?

- Open an issue for questions about architecture or design
- Check existing issues and PRs for similar work
- Reach out to maintainers for guidance

Thank you for contributing to Copinance OS! 🚀
