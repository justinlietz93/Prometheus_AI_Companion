# Prometheus AI Prompt Generator - Translation Guide

This guide provides comprehensive instructions for contributing translations to the Prometheus AI Prompt Generator project. By following these guidelines, you can help make this application accessible to users around the world.

## Table of Contents
1. [Translation Process](#translation-process)
2. [Translation Tools](#translation-tools)
3. [Style Guide](#style-guide)
4. [Continuous Integration](#continuous-integration)
5. [Web Interface for Translations](#web-interface-for-translations)

## Translation Process

The Prometheus AI Prompt Generator uses Qt's internationalization system. The workflow for translating the application is as follows:

### 1. Extract Strings for Translation

The development team regularly extracts translatable strings from the source code using the `pylupdate6` tool. This creates/updates `.ts` (translation source) files for each supported language in the `prometheus_prompt_generator/resources/translations/` directory.

### 2. Translate Strings

Translators use Qt Linguist to edit the `.ts` files, providing translations for each string. The process is as follows:

1. Open the `.ts` file for your target language in Qt Linguist
2. Go through each untranslated string and provide a translation
3. Mark translations as "done" when completed
4. Save the file

### 3. Release Translation Files

The development team compiles the `.ts` files into `.qm` (Qt Message) binary files using the `lrelease` tool. These are the files used by the application at runtime.

## Translation Tools

### Qt Linguist

[Qt Linguist](https://doc.qt.io/qt-6/linguist-translators.html) is the primary tool for translating strings. It provides a user-friendly interface for working with `.ts` files.

#### Installation

- **Windows**: Download from the [Qt website](https://www.qt.io/download-qt-installer)
- **macOS**: Install via Homebrew: `brew install qt6`
- **Linux**: Install the appropriate package for your distribution (e.g., `sudo apt install qttools5-dev-tools`)

#### Basic Usage

1. Launch Qt Linguist
2. Open the `.ts` file for your language
3. Navigate through the strings using the sidebar
4. Enter translations in the translation pane
5. Use the "Mark as 'done'" button when a translation is complete
6. Save your work frequently

### Command-Line Tools

For developers and advanced users, the following command-line tools are available:

- `pylupdate6`: Extracts translatable strings from Python code
- `lrelease`: Compiles `.ts` files into `.qm` files

## Style Guide

### General Guidelines

1. **Maintain Consistency**: Use consistent terminology throughout the translation
2. **Respect Placeholders**: Do not change placeholders such as `%1`, `%2`, or variables enclosed in curly braces
3. **Preserve Keyboard Shortcuts**: If a string contains a keyboard shortcut (e.g., `&File`), maintain the shortcut in a sensible position for your language
4. **Match Sentence Structure**: When possible, try to match the sentence structure of the original
5. **Consider Context**: Pay attention to the context information provided in Qt Linguist

### Language-Specific Guidelines

#### German (de)
- Use formal "Sie" for addressing the user
- Follow German capitalization rules for nouns
- Use "ss" instead of "ß" for better readability in UI elements

#### Spanish (es)
- Use "tú" (informal) consistently for addressing the user
- Include both masculine and feminine forms where appropriate (e.g., "usuario/a")

#### French (fr)
- Use formal "vous" for addressing the user
- Include spaces before colon, semicolon, exclamation point, and question mark
- Respect French quotation marks (« »)

### Prioritization

When translating, focus on completing strings in this order:
1. Main UI elements (menus, buttons, dialogs)
2. Common error messages
3. Help text and documentation
4. Less common features

## Continuous Integration

The project uses continuous integration to validate translations:

### Automatic Validation

When you submit a pull request with translation changes, the CI system will:

1. Check for any malformed XML in `.ts` files
2. Verify that placeholders are preserved
3. Check for missing translations in critical UI elements
4. Generate a validation report

### How to Fix Validation Errors

If the CI system reports errors in your translation:

1. Check the validation report for details
2. Open the `.ts` file in Qt Linguist
3. Navigate to the problematic strings
4. Fix the issues
5. Commit and push the changes

## Web Interface for Translations

For contributors who prefer not to install Qt Linguist, we provide a web interface for translations:

### Accessing the Web Interface

1. Go to [https://prometheus-translator.example.com](https://prometheus-translator.example.com)
2. Log in with your GitHub account or create a translator account
3. Select the language you want to work on

### Using the Web Interface

The web interface provides:
- A list of all translatable strings
- Current translation status for each language
- Context information for each string
- Suggestions from machine translation
- A discussion forum for translation questions

### Submitting Translations

1. Find untranslated or needs-review strings using the filters
2. Provide translations in the text fields
3. Click "Submit" to save your work
4. Once a significant amount is completed, click "Create Pull Request"

## Getting Help

If you have questions about translation:

1. Check the [Translation FAQ](https://github.com/prometheus-ai/prompt-generator/wiki/Translation-FAQ)
2. Ask in the #translation channel on our [Discord server](https://discord.gg/prometheus-ai)
3. File an issue on GitHub with the "translation" label

Thank you for helping make the Prometheus AI Prompt Generator accessible to users worldwide! 