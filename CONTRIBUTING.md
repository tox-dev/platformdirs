# Contributing to platformdirs

Thank you for your interest in contributing to platformdirs! This document provides guidelines and instructions for
contributing to the project.

## Code of Conduct

Be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## Getting Started

This project uses [tox](https://tox.wiki) for all development tasks. Tox provides isolated environments for testing,
linting, type checking, and documentation building.

To install tox, run:

```bash
pip install tox
```

To see all available tox environments, run:

```bash
tox list
```

## Development Workflow

### Running Tests

Run tests for a specific Python version with `tox r -e 3.14`. To run tests across multiple Python versions, use
`tox r -e 3.13,3.14`. Running `tox r` will execute all test environments.

### Code Quality Checks

Use `tox r -e fix` to auto-fix formatting and linting issues using ruff. Run `tox r -e type` to check types with
pyright.

### Coverage

The `coverage` environment combines results from previous test runs and generates reports. Run tests first with specific
Python versions, then add `coverage` to the command, for example `tox r -e 3.14,3.13,3.12,coverage`. This generates HTML
coverage reports in `.tox/htmlcov/` and checks coverage diff against `origin/main`.

### Documentation

Build and check documentation with `tox r -e docs`. The built documentation will be available in
`.tox/docs_out/html/index.html`.

### Package Metadata

Validate package metadata and build artifacts with `tox r -e pkg_meta`. This checks that the package description renders
correctly on PyPI and validates wheel contents.

### Development Environment

Set up a development environment with all dependencies with `tox r -e dev`. This creates an editable install with all
development dependencies in `.tox/dev/`.

### Running Everything

Before submitting a pull request, run `tox r` to execute all checks. This runs tests across all supported Python
versions and performs all quality checks.

## Making Changes

### Fork and Branch

Start by forking the repository on GitHub, then clone your fork locally. Create a branch from `main` with a descriptive
name such as `fix/issue-123` for bug fixes, `feat/new-directory-type` for features, or `docs/improve-readme` for
documentation changes.

### Code Style

Follow existing code patterns in the codebase. All code must pass `tox r -e fix` for ruff formatting and linting. Add
type annotations to all new code, which are checked by `tox r -e type`. Keep functions focused and well-named, and
prefer explicit over implicit code.

### Testing

Add tests for all new features and bug fixes. Tests must pass on all supported Python versions. To check coverage across
multiple Python versions, run `tox r -e 3.14,3.13,3.12,coverage` to execute tests and then combine coverage results. We
target 100% code coverage.

### Documentation

When making user-facing changes, update relevant `.rst` files in `docs/`. Add docstrings to new public functions. Update
examples if behavior changes. Run `tox r -e docs` to verify documentation builds.

## Submitting Changes

### Commit Messages

Follow Commitizen conventions with the format `<type>: <summary>` and an optional body explaining the motivation and
approach. Common types are `feat`, `fix`, `docs`, `refactor`, and `test`. For example:

```
fix: handle missing XDG_RUNTIME_DIR on FreeBSD

Falls back to /var/run/user/<uid> when /run/user/<uid> does not exist,
addressing issues on FreeBSD systems that don't create the runtime directory.
```

### Pull Requests

Ensure `tox r` passes on your branch before pushing. Push to your fork and open a pull request against `main`. Fill in
the PR template with a clear description of changes, related issue numbers, and testing performed. Wait for CI checks to
complete and address any review feedback.

## Platform-Specific Development

When adding platform-specific functionality, test on the target platform. Document behavior in `docs/platforms.rst` and
follow existing patterns for the platform by checking `src/platformdirs/<platform>.py`. Consider environment variable
overrides if applicable.

## Getting Help

Check existing [issues](https://github.com/tox-dev/platformdirs/issues) and review the
[documentation](https://platformdirs.readthedocs.io) before asking. Open a new issue for bugs or feature requests.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
