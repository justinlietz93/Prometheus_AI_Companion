# Prometheus AI Prompt Generator

A professional desktop application for generating AI prompts with different urgency levels.

## Overview

This project provides three main components:

1. **Prompt Extraction Tool**: A script to extract prompts from existing Python files and convert them to JSON format in a prompt library.
2. **Prompt Generator GUI (Tkinter)**: A basic GUI application to select and generate prompts from the library.
3. **Prometheus AI Generator (PyQt6)**: A professional GUI application with dark mode support and enhanced UI/UX.

## Migration to JSON Prompt Library

To convert the existing prompt Python files to JSON format:

1. Run the extraction script:
```bash
python extract_prompts.py
```

2. The script will:
   - Find all Python files with prompt generation functions
   - Extract prompts for levels 1-10 from each file
   - Save them as JSON in `prompt_library/prompts/`
   - Optionally delete the original prompt files if successful

## Using the GUI Applications

### Basic Version (Tkinter)

```bash
python prompt_generator_app.py
```

### Prometheus AI Version (Recommended)

For a professional interface with Prometheus AI branding and dark mode support:

```bash
python prompt_generator_qt.py
```

#### Prometheus AI Features:
- Professional UI with Prometheus AI branding
- Dark mode by default (with light mode toggle)
- Modern, responsive UI with splitter for adjustable panels
- HTML-formatted output with styled prompts
- Status bar with helpful messages
- Proper popup notifications
- Improved scrolling and selection behavior

## Requirements

### Basic Version (Tkinter)
- Python 3.5 or newer
- Tkinter (included with most Python installations)

### Prometheus AI Version (PyQt6)
- Python 3.5 or newer
- PyQt6: `pip install PyQt6>=6.8.1`

## Features

- Modular storage of prompts in JSON format
- Select multiple prompt types to generate at once
- Adjust urgency level with a slider (1-10)
- View generated prompts in a scrollable text area
- Copy generated prompts to clipboard with one click
- Dark/light mode toggle (Prometheus AI version)
- Persistent settings (Prometheus AI version)

## Project Structure

- `extract_prompts.py` - Script to extract prompts from Python files to JSON
- `prompt_generator_app.py` - Basic Tkinter GUI application
- `prompt_generator_qt.py` - Prometheus AI PyQt6 application
- `prompt_library/` - Package containing the prompt library
  - `prompt_loader.py` - Loads and provides access to JSON prompt files
  - `prompts/` - Directory containing JSON prompt files

## Adding New Prompts

To add new prompts to the library:

1. Create a new JSON file in `prompt_library/prompts/` with the format:
```json
{
  "name": "your_prompt_type",
  "description": "Description of your prompt type",
  "prompts": {
    "1": "Low urgency prompt text...",
    "2": "...",
    "10": "High urgency prompt text..."
  }
}
```

2. The application will automatically detect and include your new prompt type on next run.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## About Prometheus AI

Prometheus AI is an advanced prompt generation system designed to create effective prompts at varying urgency levels for a wide range of scenarios. 