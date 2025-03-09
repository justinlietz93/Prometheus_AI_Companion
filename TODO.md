# Prometheus AI Prompt Generator - Refactoring TODO

This document outlines the tasks needed to complete the refactoring of the Prometheus AI Prompt Generator.

## Project Organization

- [x] Create initial package structure (prometheus_prompt_generator)
- [x] Create UI module structure
- [x] Create utils module structure
- [x] Create initial compatibility layer (prompt_generator_qt.py)
- [x] Move all utility modules from prompt_library/ to prometheus_prompt_generator/utils
  - [x] Evaluate and migrate prompt_loader.py
  - [x] Evaluate and migrate prompt_manager.py
  - [x] Evaluate and migrate base_prompt.py
- [x] Integrate utils/draw_map.py if relevant
- [x] Remove duplicate files from root directory
  - [x] constants.py
  - [x] utils.py
  - [x] prompt_library.py
  - [x] metadata_dialog.py
  - [x] prompt_list_item.py
  - [x] main_window.py
  - [x] script files (standardize_*.py, extract_prompts.py, etc.)
- [x] Migrate prompt data
  - [x] Copy prompts directory to prometheus_prompt_generator/data/prompts
  - [x] Copy rules directory to prometheus_prompt_generator/data/rules
  - [x] Update prompt loader to use new paths

## Code Quality

- [ ] Add proper docstrings to all modules
- [ ] Add type hints to function signatures
- [ ] Ensure consistent code style across all modules
- [ ] Add error handling for edge cases
- [ ] Fix any remaining bugs from the modularization

## Documentation

- [x] Update README.md with new structure
- [x] Document installation procedure
- [x] Document development workflow
- [x] Create architecture overview

## Testing

- [ ] Create test directory
- [ ] Write unit tests for utils modules
- [ ] Write integration tests for UI components
- [ ] Ensure tests run on CI pipeline

## Improvements

- [ ] Fix QPixmap error in search widget
- [ ] Review enhancements.txt for further goals
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