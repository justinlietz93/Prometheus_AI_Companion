# Qt Designer Integration for Prometheus AI Prompt Generator

This document explains how to use Qt Designer with the Prometheus AI Prompt Generator application to create and modify UI components.

## Overview

Qt Designer is a powerful tool for creating and modifying user interfaces in Qt applications. By using Qt Designer, we can:

1. Visually design UI components without writing code
2. Easily modify layouts and widget properties
3. Separate UI design from application logic
4. Make UI changes without modifying Python code

## Getting Started

### Prerequisites

- PyQt6 installed (`pip install PyQt6`)
- Qt Designer installed (comes with PyQt6 or can be installed separately)
- pyuic6 tool available (part of PyQt6)

### Directory Structure

The Qt Designer files are organized as follows:

```
prometheus_prompt_generator/
├── ui/
│   ├── designer/
│   │   ├── main_window.ui        # Main window UI file
│   │   ├── ui_main_window.py     # Generated Python code from UI file
│   │   ├── metadata_dialog.ui    # Metadata dialog UI file
│   │   └── ui_metadata_dialog.py # Generated Python code from UI file
```

## Using the UI Files

There are two main approaches to using Qt Designer UI files in your application:

### 1. Composition Approach

This approach loads the UI file at runtime:

```python
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI file
        ui_file_path = "path/to/main_window.ui"
        self.ui = uic.loadUi(ui_file_path, self)
        
        # Access widgets through self.ui
        self.ui.generatePromptsButton.clicked.connect(self.on_generate_prompts)
```

### 2. Inheritance Approach

This approach uses the Python code generated from the UI file:

```python
from PyQt6.QtWidgets import QMainWindow
from prometheus_prompt_generator.ui.designer.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup the UI
        self.setupUi(self)
        
        # Access widgets directly
        self.generatePromptsButton.clicked.connect(self.on_generate_prompts)
```

## Generating UI Files

We provide two scripts to help with Qt Designer integration:

### 1. Generate UI File

The `scripts/generate_ui_file.py` script creates a Qt Designer UI file based on the current hand-coded UI:

```bash
python scripts/generate_ui_file.py
```

This will generate a `main_window.ui` file in the `prometheus_prompt_generator/ui/designer/` directory.

### 2. Use Designer UI

The `scripts/use_designer_ui.py` script demonstrates how to use the generated UI file with both composition and inheritance approaches:

```bash
python scripts/use_designer_ui.py
```

This will:
1. Generate the UI file if it doesn't exist
2. Convert the UI file to Python code using pyuic6
3. Create two windows demonstrating both approaches

## Modifying UI Files

To modify the UI files:

1. Open Qt Designer:
   ```bash
   designer
   ```

2. Open the UI file:
   ```
   prometheus_prompt_generator/ui/designer/main_window.ui
   ```

3. Make your changes and save the file

4. Convert the UI file to Python code:
   ```bash
   pyuic6 prometheus_prompt_generator/ui/designer/main_window.ui -o prometheus_prompt_generator/ui/designer/ui_main_window.py
   ```

## Best Practices

1. **Keep UI and Logic Separate**: Use the UI files for layout and appearance, and keep application logic in your Python code.

2. **Don't Modify Generated Code**: Never modify the generated Python files (ui_*.py) directly. Always modify the UI files and regenerate the Python code.

3. **Use Object Names**: Give meaningful object names to widgets in Qt Designer so they're easy to reference in your code.

4. **Use Layouts**: Always use layouts in Qt Designer to ensure your UI is responsive and resizes properly.

5. **Signal/Slot Connections**: Connect signals to slots in your Python code, not in Qt Designer.

## Troubleshooting

### UI File Not Found

If you get an error about the UI file not being found, make sure you're running the script from the correct directory or provide the full path to the UI file.

### pyuic6 Not Found

If you get an error about pyuic6 not being found, make sure it's installed and in your PATH. It should be installed with PyQt6.

### Widgets Not Accessible

If you're using the composition approach and can't access widgets, make sure you're using `self.ui.widgetName`. If you're using the inheritance approach, you can access widgets directly with `self.widgetName`.

## Resources

- [Qt Designer Manual](https://doc.qt.io/qt-6/qtdesigner-manual.html)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Using a Designer UI File in Python](https://doc.qt.io/qt-6/designer-using-a-ui-file-python.html) 