```markdown
# spine Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `spine` Python codebase. It covers file organization, code style, commit practices, and testing patterns, enabling contributors to write consistent, maintainable code and collaborate effectively.

## Coding Conventions

### File Naming
- Use **snake_case** for all file and module names.
  - Example: `data_loader.py`, `utils/helpers.py`

### Import Style
- Prefer **relative imports** within the package.
  - Example:
    ```python
    from .utils import process_data
    ```

### Export Style
- Use **named exports**; explicitly define what is exported from modules.
  - Example:
    ```python
    __all__ = ['process_data', 'DataLoader']
    ```

### Commit Messages
- Follow **conventional commit** format.
- Use the `feat` prefix for new features.
  - Example: `feat: add support for batch data processing`

## Workflows

### Feature Development
**Trigger:** When adding a new feature to the codebase  
**Command:** `/feature-development`

1. Create a new branch for your feature.
2. Implement the feature following coding conventions.
3. Add or update tests as needed.
4. Commit changes using the `feat` prefix and a descriptive message.
   - Example: `feat: implement user authentication`
5. Push your branch and open a pull request for review.

### Testing
**Trigger:** When verifying code correctness or before submitting a pull request  
**Command:** `/run-tests`

1. Identify or create test files matching the `*.test.*` pattern.
2. Run tests using the project's preferred test runner (framework is unknown; consult project docs or use `pytest` as a default).
   - Example: `pytest`
3. Ensure all tests pass before merging or submitting code.

## Testing Patterns

- Test files are named using the `*.test.*` pattern (e.g., `module.test.py`).
- The specific testing framework is not specified; use standard Python testing frameworks such as `unittest` or `pytest` unless otherwise directed.
- Place test files alongside the modules they test or in a dedicated `tests/` directory.

## Commands
| Command              | Purpose                                 |
|----------------------|-----------------------------------------|
| /feature-development | Start a new feature workflow            |
| /run-tests           | Run the test suite                      |
```
