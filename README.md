# Prometheus AI Prompt Generator

A professional desktop application for generating AI prompts with different urgency levels using the prompt library, built with PyQt6 with dark mode support.

## Features

- Modern, responsive UI with dark and light themes
- Searchable prompt library with multiple prompt categories
- Customizable urgency levels for each prompt
- Import and export prompts as JSON
- Copy generated prompts to clipboard
- Add custom prompts with metadata
- Themes and font customization

## Project Structure

The project follows a modular design for maintainability and scalability:

```
prometheus_prompt_generator/
├── __init__.py              # Package exports
├── ui/                      # UI Components
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── metadata_dialog.py   # Dialog for editing prompt metadata
│   └── prompt_list_item.py  # Custom widget for prompt list items
└── utils/                   # Utilities
    ├── __init__.py
    ├── constants.py         # Application constants
    ├── prompt_library.py    # Prompt management functionality
    └── utils.py             # Helper functions

main.py                      # Application entry point
prompt_generator_qt.py       # Compatibility layer for backward compatibility
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prometheus-prompt-generator.git
cd prometheus-prompt-generator
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the requirements:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

### Generating Prompts

1. Select one or more prompt types from the left panel
2. Adjust the urgency level using the slider
3. Click "Generate Prompts"
4. The generated prompts will appear in the text area
5. Copy the prompts to clipboard with the "Copy to Clipboard" button

### Adding Custom Prompts

1. Click "Add Custom Prompt"
2. Enter a unique identifier for the prompt
3. Enter a display name
4. Enter the prompt template with {placeholders} for variables
5. Click "OK" to save the prompt

### Customizing Appearance

- **Change Theme**: Edit → Theme → (Select a theme)
- **Change Font**: Edit → Change Font...
- **Reset Font**: Edit → Reset Font

## Development

### Requirements

- Python 3.8+
- PyQt6
- qt-material

### Adding New Prompt Types

Create JSON files in the `prompt_library/prompts` directory with the following structure:

```json
{
  "title": "My Custom Prompt",
  "description": "A description of what this prompt does",
  "template": "Your prompt template with {placeholders} for variables",
  "metadata": {
    "author": "Your Name",
    "version": "1.0.0",
    "created": "2023-03-09",
    "updated": "2023-03-09",
    "tags": ["custom", "tag1", "tag2"]
  }
}
```

## License

[MIT License](LICENSE) 