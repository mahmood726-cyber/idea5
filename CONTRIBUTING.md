# Contributing to Publication Bias Assessment Dashboard

Thank you for your interest in contributing! This document provides guidelines for contributions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Code sample if applicable

### Suggesting Enhancements

1. Check existing issues and pull requests
2. Create an issue describing:
   - The enhancement
   - Why it would be useful
   - Possible implementation approach

### Code Contributions

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes**:
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Test your changes**: `pytest tests/`
5. **Commit**: Use clear, descriptive commit messages
6. **Push**: `git push origin feature/your-feature-name`
7. **Create Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/publication-bias-dashboard.git
cd publication-bias-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all functions/classes
- Maximum line length: 100 characters

Example:
```python
def example_function(param1: int, param2: str) -> float:
    """
    Brief description.

    Parameters:
        param1: Description
        param2: Description

    Returns:
        Description of return value
    """
    pass
```

## Testing

- Write unit tests for new methods
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
# Run tests with coverage
pytest --cov=src tests/
```

## Adding New Methods

To add a new publication bias method:

1. **Create method file**: `src/methods/your_method.py`
2. **Implement method** with clear docstrings
3. **Add tests**: `tests/test_your_method.py`
4. **Update** `src/methods/__init__.py`
5. **Add to dashboard**: Update `src/dashboard/app.py`
6. **Document**: Add description to README and paper template

## Documentation

- Update README.md for user-facing changes
- Update QUICKSTART.md for new features
- Add examples to `examples/` if appropriate
- Update paper template if implementing new method

## Pull Request Process

1. Update README.md with details of changes
2. Update version numbers if appropriate
3. PR will be merged once you have approval from maintainers

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Publishing others' private information
- Other unethical or unprofessional conduct

## Questions?

Feel free to open an issue or contact the maintainers.

Thank you for contributing! 🎉
