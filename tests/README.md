# Testing Framework for Prometheus AI Prompt Generator

This directory contains the test suite for the Prometheus AI Prompt Generator project, following Test-Driven Development (TDD) principles.

## TDD Workflow

1. **Write Tests First**: Before implementing any feature, write tests that define the expected behavior.
2. **Verify Tests Fail**: Ensure tests fail initially (they should, as you haven't implemented the feature yet).
3. **Implement the Feature**: Write the minimal code needed to make the tests pass.
4. **Run Tests**: Verify that your implementation passes the tests.
5. **Refactor**: Clean up and optimize your code while keeping tests passing.

## Directory Structure

- `conftest.py`: Common test fixtures and configuration shared across all tests
- `unit/`: Tests for individual components in isolation
  - `domain/`: Domain layer tests
    - `models/`: Tests for domain models
    - `controllers/`: Tests for controllers (business logic)
- `integration/`: Tests that verify different components work together

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=prometheus_prompt_generator
```

To run a specific test file:

```bash
pytest tests/unit/domain/controllers/test_prompt_controller.py
```

## Testing Standards

1. **Test Coverage**: Aim for at least 90% code coverage.
2. **Test Isolation**: Unit tests should not depend on external systems.
3. **Naming Convention**: Test methods should be named `test_[feature]_[scenario]`.
4. **Assertions**: Each test should have clear assertions that verify the expected behavior.
5. **Mocking**: Use mocks for external dependencies to ensure test isolation.

## Measuring Success

For Test-Driven Development, success is measured by:

1. **Passing Tests**: All tests pass consistently.
2. **Code Coverage**: Test coverage exceeds 90% for all components.
3. **Regression Prevention**: Changes don't break existing functionality.
4. **Documentation**: Tests serve as documentation for expected behavior.

Remember: Test-Driven Development is about defining what success looks like before you start coding. 