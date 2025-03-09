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

## UI Enhancements

- [x] Fix QPixmap error in search widget
- [x] Implement 10 levels of urgency in the slider
- [x] Fix the selector window to show all text and tags
- [x] Add info icon for metadata display
- [x] Make editor window editable
- [x] Clean up generated prompt output
- [x] Move Generate Prompts button next to Copy to Clipboard
- [x] Update search icon to modern style
- [x] Implement overall modern IDE-like UI improvements

## Qt Architecture Improvements

- [x] Create scripts for Qt Designer integration
  - [x] Create script to generate UI file from current layout
  - [x] Create example script demonstrating both composition and inheritance approaches
- [ ] Convert UI to Qt Designer (.ui) files
  - [ ] Create main window UI in Qt Designer
  - [ ] Create dialog UIs in Qt Designer 
  - [ ] Setup pyuic6 conversion process
- [ ] Implement proper QMainWindow structure
  - [ ] Refactor menu system using Qt menu standards
  - [ ] Add proper status bar with context information
  - [ ] Implement dockable widget areas if needed
- [ ] Add internationalization support
  - [ ] Setup pylupdate6 to extract translatable strings
  - [ ] Create .ts translation files
  - [ ] Add language switching mechanism
- [ ] Implement resource management
  - [ ] Create .qrc resource file for icons and assets
  - [ ] Setup pyrcc6 conversion process
  - [ ] Use QResource system for all assets

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

## User Experience

- [ ] Add dialog-based help system 
  - [ ] Implement context-sensitive help using Qt Assistant patterns
  - [ ] Create comprehensive help documentation
- [ ] Add keyboard shortcuts for common actions
- [ ] Implement customizable themes with color selection
- [ ] Add persistent user settings storage
- [ ] Implement proper error handling dialogs

## Release Preparation

- [ ] Create setup.py for packaging
- [ ] Add version management
- [ ] Create release scripts
- [ ] Update requirements.txt 