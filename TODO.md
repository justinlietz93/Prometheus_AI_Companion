# Prometheus AI Prompt Generator - Refactoring TODO

This document outlines the tasks needed to complete the refactoring of the Prometheus AI Prompt Generator.

## Project Organization

- [x] Create initial package structure (prometheus_prompt_generator)
- [x] Create UI module structure
- [x] Create utils module structure
- [x] Create initial compatibility layer (prompt_generator_qt.py)
- [ ] Move all utility modules from prompt_library/ to prometheus_prompt_generator/utils
  - [ ] Evaluate and migrate prompt_loader.py
  - [ ] Evaluate and migrate prompt_manager.py
  - [ ] Evaluate and migrate base_prompt.py
- [ ] Integrate utils/draw_map.py if relevant
- [ ] Remove duplicate files from root directory
  - [ ] constants.py
  - [ ] utils.py
  - [ ] prompt_library.py
  - [ ] metadata_dialog.py
  - [ ] prompt_list_item.py
  - [ ] main_window.py

## Code Quality

- [ ] Add proper docstrings to all modules
- [ ] Add type hints to function signatures
- [ ] Ensure consistent code style across all modules
- [ ] Add error handling for edge cases
- [ ] Fix any remaining bugs from the modularization

## Documentation

- [x] Update README.md with new structure
- [ ] Document installation procedure
- [ ] Document development workflow
- [ ] Create architecture overview

## Testing

- [ ] Create test directory
- [ ] Write unit tests for utils modules
- [ ] Write integration tests for UI components
- [ ] Ensure tests run on CI pipeline

## Improvements

- [ ] Fix QPixmap error in search widget
- [ ] Add consistent icons for buttons and menus
- [ ] Improve theme handling and customization
- [ ] Add keyboard shortcuts for common actions
- [ ] Add proper logging framework
- [ ] Add more robust error handling

## Release Preparation

- [ ] Create setup.py for packaging
- [ ] Add version management
- [ ] Create release scripts
- [ ] Update requirements.txt 