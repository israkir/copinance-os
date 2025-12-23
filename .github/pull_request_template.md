## Description

<!-- Provide a clear and concise description of what this PR does and why it's needed -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test additions or updates
- [ ] 🔨 Build/config changes
- [ ] 🎨 Style/formatting changes

## Related Issues

<!-- Link related issues using keywords: fixes, closes, resolves -->
<!-- Example: Fixes #123, Closes #456 -->

Fixes #
Closes #
Related to #

## Changes Made

<!-- Provide a detailed list of changes -->

-
-
-

## Testing

<!-- Describe the tests you ran and how to verify your changes -->

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Tests cover both success and error cases
- [ ] Integration tests updated (if applicable)

### Test Commands
```bash
# Add commands to run tests
pytest
pytest -m unit
pytest -m integration
```

## Code Quality

<!-- Confirm that code quality checks pass -->

- [ ] Code is formatted with `black`
- [ ] Linting passes with `ruff`
- [ ] Type checking passes with `mypy`
- [ ] No new warnings or errors introduced

### Code Quality Commands
```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

## Documentation

<!-- Confirm documentation is updated -->

- [ ] README updated (if applicable)
- [ ] Docstrings added/updated for new functions/classes
- [ ] Architecture docs updated (if applicable)
- [ ] CHANGELOG updated (for significant changes)
- [ ] API documentation updated (if applicable)

## Architecture Compliance

<!-- For significant changes, confirm architecture guidelines are followed -->

- [ ] Follows clean architecture principles
- [ ] Domain layer remains dependency-free
- [ ] Proper dependency injection used
- [ ] Interfaces defined in domain/ports (if adding new functionality)
- [ ] Implementation in appropriate infrastructure layer

## Screenshots/Examples

<!-- If applicable, add screenshots or examples to help explain your changes -->

## Checklist

<!-- Complete all relevant items -->

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

<!-- Add any additional context, notes, or considerations for reviewers -->

## Reviewer Notes

<!-- Any specific areas you'd like reviewers to focus on -->
