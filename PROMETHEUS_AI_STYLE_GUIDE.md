# Prometheus AI Style Guide

## Overview

This style guide defines the standards for Prometheus AI applications, prompt files, and related content to ensure consistent branding, user experience, and code quality.

## 1. Naming Conventions

### 1.1 File Naming

- **Python Files**: Use lowercase with underscores (snake_case)
  - Example: `prompt_generator_qt.py`, `prompt_loader.py`

- **JSON Prompt Files**: Use lowercase with underscores, no "_prompt" suffix
  - Example: `code_review.json`, `debugging.json`

- **UI Files**: Use lowercase with underscores, with `.ui` extension
  - Example: `main_window.ui`, `prompt_viewer.ui`

### 1.2 Code Naming

- **Classes**: Use CamelCase (also known as PascalCase)
  - Example: `PrometheusPromptGenerator`, `PromptLibrary`

- **Methods and Functions**: Use lowercase with underscores (snake_case)
  - Example: `generate_prompts()`, `load_prompt_file()`

- **Variables**: Use lowercase with underscores (snake_case)
  - Example: `urgency_level`, `prompt_types`

- **Constants**: Use uppercase with underscores
  - Example: `PROMETHEUS_RED`, `DEFAULT_AUTHOR`

## 2. JSON Format Standards

### 2.1 Structure

All prompt JSON files must follow this structure:

```json
{
  "name": "prompt_type",
  "description": "Capitalized Description Of The Prompt Type",
  "metadata": {
    "author": "Prometheus AI",
    "version": "1.0.0",
    "created": "YYYY-MM-DD",
    "tags": ["ai", "prompt", "prompt_type"]
  },
  "prompts": {
    "1": "Lowest urgency prompt text...",
    "2": "...",
    "3": "...",
    "4": "...",
    "5": "Medium urgency prompt text...",
    "6": "...",
    "7": "...",
    "8": "...",
    "9": "...",
    "10": "Highest urgency prompt text..."
  }
}
```

### 2.2 Required Fields

- `name`: Must match the filename (without extension)
- `description`: A human-readable description of the prompt type
- `metadata`: Contains author, version, creation date, and tags
- `prompts`: A dictionary of prompts with string keys representing urgency levels (1-10)

## 3. Branding and Theme Guidelines

### 3.1 Colors

- **Primary Color**: Prometheus Red - RGB(220, 53, 69) / #DC3545
- **Background Dark**: RGB(33, 37, 41) / #212529
- **Background Light**: RGB(248, 249, 250) / #F8F9FA
- **Accent Color**: RGB(255, 193, 7) / #FFC107

### 3.2 Typography

- **Headers**: Arial Bold, 18pt for main headings
- **Body Text**: System default font, 10-12pt
- **Buttons**: System default font, 10pt

### 3.3 Logo Usage

- Include the Prometheus AI logo in the header of all applications
- Maintain clear space around the logo equal to the height of the "P" in "Prometheus"
- Do not stretch, distort, or change the colors of the logo

## 4. UI/UX Standards

### 4.1 Layout Guidelines

- Use consistent spacing (8px, 16px, 24px, 32px)
- Maintain a clear visual hierarchy
- Use QSplitter for resizable panels
- Include status bar for user feedback
- Provide clear error messages

### 4.2 Interaction Guidelines

- All actions should provide immediate visual feedback
- Critical actions should have confirmation dialogs
- Include keyboard shortcuts for common actions
- Support clipboard operations for prompt text

### 4.3 Accessibility

- Use sufficient color contrast (minimum 4.5:1 for normal text)
- Support keyboard navigation
- Include tool tips for all interactive elements
- Test with screen readers

## 5. Code Style

### 5.1 Python Style

- Follow PEP 8 style guide
- Use docstrings for all classes and functions
- Include type hints where appropriate
- Maximum line length of 100 characters

### 5.2 Comments

- Use comments to explain "why," not "what"
- Include a header comment in each file explaining its purpose
- Comment complex algorithms and business logic

### 5.3 Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application imports
- Use absolute imports rather than relative imports

## 6. Prompt Writing Guidelines

### 6.1 Urgency Levels

- **Level 1-3**: Low urgency, informational, routine
- **Level 4-6**: Medium urgency, important but not critical
- **Level 7-9**: High urgency, requires prompt attention
- **Level 10**: Critical, requires immediate action

### 6.2 Tone and Voice

- Professional and clear
- Concise but complete
- Active voice
- Consistent terminology

### 6.3 Structure

- Begin with the user's role or responsibility
- State the situation or context
- Provide clear direction or request
- End with expected outcome or deadline if applicable

## 7. Version Control Standards

### 7.1 Commit Guidelines

- Use clear, descriptive commit messages
- Begin with a verb in the present tense
- Keep commits focused on a single change
- Reference issue numbers in commit messages

### 7.2 Branching

- Use feature branches for new development
- Use hotfix branches for urgent fixes
- Merge through pull requests with code review

## 8. Application Features

All Prometheus AI applications should include:

- Dark/light mode toggle
- Copy to clipboard functionality
- Clear error handling
- Version display
- Status bar with helpful messages
- Consistent keyboard shortcuts

---

This style guide is maintained by Prometheus AI and should be followed for all projects and contributions.

Last Updated: 2023 