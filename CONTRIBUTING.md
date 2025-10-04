# Contributing to Lightweight Framework

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/lightweight-framework.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for all public functions and classes
- Keep functions small and focused

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=framework
```

## Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Update examples if relevant

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Questions?

Feel free to open an issue for any questions or concerns.
