# Contributing to platformdirs

Thank you for your interest in contributing to platformdirs! This document provides guidelines and instructions for
contributing to the project.

## Code of Conduct

Be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## Getting Started

This project uses [tox](https://tox.wiki/en/4.35.0) for all development tasks. Tox provides isolated environments for
testing, linting, type checking, and documentation building.

### Install tox

```bash
pip install tox
```

### Available Environments

List all available tox environments:

```bash
tox list
```

## Development Workflow

### Running Tests

Run tests for a specific Python version:

```bash
tox r -e 3.14
```

Run tests for multiple Python versions:

```bash
tox r -e 3.13,3.14
```

Run all test environments:

```bash
tox r
```

### Code Quality Checks

Auto-fix formatting and linting issues:

```bash
tox r -e fix
```

Run type checking:

```bash
tox r -e type
```

### Coverage

Combine coverage from all test runs and generate reports:

```bash
tox r -e coverage
```

This generates HTML coverage reports in `.tox/htmlcov/` and checks coverage diff against `origin/main`.

### Documentation

Build and check documentation:

```bash
tox r -e docs
```

The built documentation will be available in `.tox/docs_out/html/index.html`.

### Package Metadata

Validate package metadata and build artifacts:

```bash
tox r -e pkg_meta
```

This checks that the package description renders correctly on PyPI and validates wheel contents.

### Development Environment

Set up a development environment with all dependencies:

```bash
tox r -e dev
```

This creates an editable install with all development dependencies in `.tox/dev/`.

### Running Everything

Before submitting a PR, run all checks:

```bash
tox r
```

This runs tests across all supported Python versions and performs all quality checks.

## Making Changes

### Fork and Branch

1. Fork the repository on GitHub
1. Clone your fork locally
1. Create a branch from `main`:

```bash
git checkout -b fix/issue-123
```

Use descriptive branch names:

- `fix/issue-123` for bug fixes
- `feat/new-directory-type` for features
- `docs/improve-readme` for documentation

### Code Style

- Follow existing code patterns in the codebase
- All code must pass `tox r -e fix` (ruff formatting and linting)
- Add type annotations to all new code (checked by `tox r -e type`)
- Keep functions focused and well-named
- Prefer explicit over implicit

### Testing

- Add tests for all new features and bug fixes
- Tests must pass on all supported Python versions
- Run `tox r -e coverage` to check test coverage
- We target 100% code coverage

### Documentation

When making user-facing changes:

- Update relevant `.rst` files in `docs/`
- Add docstrings to new public functions
- Update examples if behavior changes
- Run `tox r -e docs` to verify documentation builds

## Submitting Changes

### Commit Messages

Follow Commitizen conventions:

```
<type>: <summary>

<optional body>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `build`

Example:

```
fix: handle missing XDG_RUNTIME_DIR on FreeBSD

Falls back to /var/run/user/<uid> when /run/user/<uid> does not exist,
addressing issues on FreeBSD systems that don't create the runtime directory.
```

### Pull Requests

1. Ensure `tox r` passes on your branch
1. Push to your fork
1. Open a pull request against `main`
1. Fill in the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
1. Wait for CI checks to complete
1. Address any review feedback

## Platform-Specific Development

When adding platform-specific functionality:

- Test on the target platform
- Document behavior in `docs/platforms.rst`
- Follow existing patterns for the platform (check `src/platformdirs/<platform>.py`)
- Consider environment variable overrides if applicable

## Getting Help

- Check existing [issues](https://github.com/tox-dev/platformdirs/issues)
- Review [documentation](https://platformdirs.readthedocs.io)
- Open a new issue for bugs or feature requests

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
