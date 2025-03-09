# UI Standards

## Overview

This document outlines the user interface standards for the Prometheus AI Prompt Generator. Following these guidelines ensures a consistent, intuitive, and maintainable user interface across the application while adhering to Qt best practices.

## Qt Framework Usage

The Prometheus AI Prompt Generator uses Qt 6 as its UI framework, specifically focusing on Qt Widgets for desktop application development with Python bindings via PyQt6.

## Design Principles

### Visual Hierarchy

- Establish clear visual hierarchy with primary, secondary, and tertiary elements
- Use consistent spacing (8px, 16px, 24px, 32px grid)
- Group related controls and provide visual separation between groups
- Maintain alignment of UI elements (left-aligned for labels, right-aligned for numbers)

### User Experience Guidelines

- Provide immediate feedback for user actions
- Preserve user input and state during operations
- Support keyboard navigation and shortcuts for all actions
- Follow platform-specific UI conventions
- Display clear error messages and recovery options
- Support undo/redo for all destructive operations

### Accessibility

- Ensure sufficient color contrast (minimum 4.5:1 ratio)
- Provide keyboard access to all functionality
- Use descriptive labels for screen readers
- Support system text scaling
- Design for color blindness compatibility

## Color Standards

### Color Palette

```python
# Color definitions
class PrometheusColors:
    # Primary brand colors
    PRIMARY = "#DC3545"  # Prometheus Red
    PRIMARY_LIGHT = "#E66975"
    PRIMARY_DARK = "#BD2130"
    
    # Background colors
    BG_DARK = "#212529"
    BG_LIGHT = "#F8F9FA"
    
    # Accent colors
    ACCENT = "#FFC107"  # Amber
    
    # Semantic colors
    SUCCESS = "#28A745"
    INFO = "#17A2B8"
    WARNING = "#FFC107"
    DANGER = "#DC3545"
    
    # Gray scale
    GRAY_100 = "#F8F9FA"
    GRAY_200 = "#E9ECEF"
    GRAY_300 = "#DEE2E6"
    GRAY_400 = "#CED4DA"
    GRAY_500 = "#ADB5BD"
    GRAY_600 = "#6C757D"
    GRAY_700 = "#495057"
    GRAY_800 = "#343A40"
    GRAY_900 = "#212529"
```

### Color Usage

- Use primary colors for main actions and branding
- Use accent colors sparingly to highlight important elements
- Use semantic colors to convey meaning (success, error, warning, etc.)
- Maintain consistent color usage across the application
- Ensure sufficient contrast between text and background

## Layout Guidelines

### Responsive Design

- Use layout managers (QVBoxLayout, QHBoxLayout, QGridLayout) instead of absolute positioning
- Implement proper resizing behavior for all UI components
- Use QSplitter for resizable panel areas
- Design for various screen sizes and resolutions
- Test layouts with different DPI settings

### Standard Spacing

```python
# Spacing constants
class Spacing:
    TINY = 4   # Minimal internal spacing
    SMALL = 8  # Default internal spacing
    MEDIUM = 16  # Default external spacing
    LARGE = 24  # Section spacing
    XLARGE = 32  # Major section spacing
    
    # Margins
    DEFAULT_MARGIN = 16
    DIALOG_MARGIN = 24
```

### Container Guidelines

- Use QGroupBox to group related controls
- Use QTabWidget for organizing multiple pages of settings
- Use QScrollArea for content that may exceed available space
- Apply consistent margins and padding

## Component Standards

### Form Controls

#### Text Inputs

- Provide clear labels for all input fields
- Show validation state visually (error, success)
- Use placeholder text sparingly and only for clarification
- Set appropriate tab order for form fields

```python
# Example text field with validation
class ValidatedTextField(QWidget):
    valueChanged = pyqtSignal(str)
    
    def __init__(self, label, placeholder="", required=False, parent=None):
        super().__init__(parent)
        self.required = required
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label with required indicator if needed
        label_text = label
        if required:
            label_text += " *"
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        
        # Text field
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText(placeholder)
        self.text_field.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_field)
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #DC3545; font-size: 11px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
    
    def _on_text_changed(self, text):
        self.valueChanged.emit(text)
        self.validate()
    
    def text(self):
        return self.text_field.text()
    
    def setText(self, text):
        self.text_field.setText(text)
    
    def setError(self, error_message):
        if error_message:
            self.error_label.setText(error_message)
            self.error_label.setVisible(True)
            self.text_field.setStyleSheet("border: 1px solid #DC3545;")
        else:
            self.error_label.setVisible(False)
            self.text_field.setStyleSheet("")
    
    def validate(self):
        if self.required and not self.text():
            self.setError("This field is required")
            return False
        self.setError("")
        return True
```

#### Buttons

- Use descriptive, action-oriented button text
- Make primary actions visually prominent
- Right-align dialog buttons with OK/Apply/Cancel order
- Provide tooltips for icon-only buttons
- Disable buttons when the action is unavailable

```python
# Button styling example
def apply_button_styles(button, button_type="default"):
    if button_type == "primary":
        button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #BD2130;
            }
            QPushButton:disabled {
                background-color: #E9ECEF;
                color: #6C757D;
            }
        """)
    elif button_type == "secondary":
        button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
            QPushButton:disabled {
                background-color: #E9ECEF;
                color: #6C757D;
            }
        """)
    # Other button types...
```

#### Selection Controls

- Group related checkboxes and radio buttons
- Align checkboxes and radio buttons vertically for clarity
- Use descriptive labels for each option
- Provide keyboard shortcuts for common options

### Dialog Standards

- Follow platform conventions for dialog layout and button placement
- Provide descriptive titles that explain the dialog's purpose
- Display clear error messages and confirmation prompts
- Make dialogs resizable when they contain variable content
- Support keyboard navigation (Tab, Enter, Escape)
- Use appropriate modal vs. non-modal behavior

```python
# Example dialog setup
class PromptEditorDialog(QDialog):
    def __init__(self, prompt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Prompt" if prompt else "Create Prompt")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.DIALOG_MARGIN, Spacing.DIALOG_MARGIN, 
                                 Spacing.DIALOG_MARGIN, Spacing.DIALOG_MARGIN)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(Spacing.MEDIUM)
        
        self.title_field = QLineEdit()
        if prompt:
            self.title_field.setText(prompt.title)
        form_layout.addRow("Title:", self.title_field)
        
        self.content_field = QTextEdit()
        if prompt:
            self.content_field.setText(prompt.content)
        form_layout.addRow("Content:", self.content_field)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
```

### List and Table Views

- Use appropriate view for data display (QListView, QTableView, QTreeView)
- Implement alternating row colors for better readability
- Support sorting and filtering for data tables
- Show loading state during data retrieval
- Provide empty state messaging when no data is available
- Implement pagination for large datasets

```python
# Example table setup
class PromptTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure view properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        # Set delegate for custom rendering
        self.setItemDelegate(PromptItemDelegate())
```

### Internationalization and Localization

- Use `qsTr()` or `tr()` for all user-visible strings
- Use appropriate date and number formatting for the user's locale
- Support right-to-left languages if needed
- Test with different languages to ensure layout flexibility

```python
# Example of using tr() for translation
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Translatable window title
        self.setWindowTitle(self.tr("Prometheus AI Prompt Generator"))
        
        # Translatable menu items
        file_menu = self.menuBar().addMenu(self.tr("&File"))
        file_menu.addAction(self.tr("&New"), self.new_prompt, QKeySequence.New)
        file_menu.addAction(self.tr("&Open..."), self.open_prompt, QKeySequence.Open)
        file_menu.addAction(self.tr("&Save"), self.save_prompt, QKeySequence.Save)
```

## Patterns and Best Practices

### Qt Designer Integration

- Use Qt Designer for creating form layouts
- Use `.ui` files for design and load them dynamically
- Give widgets meaningful object names for auto-connection
- Follow consistent naming patterns for widget hierarchy

```python
# Example of loading a UI file
class PromptListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load UI file
        ui_file = QFile(":/ui/prompt_list.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect signals and slots
        self.ui.add_button.clicked.connect(self.on_add_clicked)
        self.ui.remove_button.clicked.connect(self.on_remove_clicked)
        self.ui.prompt_list.itemSelectionChanged.connect(self.on_selection_changed)
```

### Model-View-ViewModel (MVVM) Pattern

- Separate UI (View) from presentation logic (ViewModel) and data (Model)
- Use Qt's Model/View architecture for data displays
- Create custom models for complex data structures
- Use QDataWidgetMapper for form binding
- Implement signal/slot connections for UI updates

```python
# Example of ViewModel implementation
class PromptViewModel(QObject):
    promptsChanged = pyqtSignal()
    selectionChanged = pyqtSignal(object)
    
    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.prompts = []
        self.selected_prompt = None
    
    def load_prompts(self):
        try:
            self.prompts = self.prompt_service.get_all_prompts()
            self.promptsChanged.emit()
        except Exception as e:
            logging.error(f"Error loading prompts: {e}")
            # Handle error
    
    def select_prompt(self, index):
        if 0 <= index < len(self.prompts):
            self.selected_prompt = self.prompts[index]
            self.selectionChanged.emit(self.selected_prompt)
        else:
            self.selected_prompt = None
            self.selectionChanged.emit(None)
```

### Error Handling and User Feedback

- Display errors in context where they occur
- Show error messages with appropriate severity
- Provide status updates for long-running operations
- Use the status bar for transient messages
- Implement toast notifications for non-blocking feedback

```python
# Example of different notification types
class NotificationManager:
    @staticmethod
    def show_success(parent, message):
        QMessageBox.information(parent, "Success", message)
    
    @staticmethod
    def show_error(parent, title, message):
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_warning(parent, title, message):
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_status_message(status_bar, message, timeout=3000):
        status_bar.showMessage(message, timeout)
    
    @staticmethod
    def confirm_action(parent, title, message):
        reply = QMessageBox.question(parent, title, message,
                                    QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes
```

### Keyboard Shortcuts

- Implement standard shortcuts for common actions (Ctrl+S, Ctrl+O, etc.)
- Provide keyboard navigation between all UI elements
- Define consistent custom shortcuts for application-specific actions
- Document all keyboard shortcuts in help documentation
- Allow customization of shortcuts if needed

```python
# Example of setting up keyboard shortcuts
def setup_shortcuts(self):
    # Standard shortcuts
    self.save_action.setShortcut(QKeySequence.Save)
    self.open_action.setShortcut(QKeySequence.Open)
    self.new_action.setShortcut(QKeySequence.New)
    self.print_action.setShortcut(QKeySequence.Print)
    
    # Custom shortcuts
    self.run_action.setShortcut(QKeySequence("Ctrl+R"))
    self.find_action.setShortcut(QKeySequence("Ctrl+F"))
    self.generate_action.setShortcut(QKeySequence("F5"))
```

## Context-Sensitive Help

Implement a comprehensive help system using Qt Assistant:

- Provide F1 help for all components
- Create context-sensitive help documentation
- Include tooltips for controls with clear descriptions
- Add "What's This" help for complex features

```python
# Example of setting up context help
def setup_help(self):
    # Create help action
    help_action = QAction(self.tr("Help Contents"), self)
    help_action.setShortcut(QKeySequence.HelpContents)  # F1
    help_action.triggered.connect(self.show_help)
    
    # Add to help menu
    help_menu = self.menuBar().addMenu(self.tr("&Help"))
    help_menu.addAction(help_action)
    
    # Set what's this text for complex widgets
    self.advanced_options.setWhatsThis(
        self.tr("Advanced options control specific LLM parameters like temperature and top-p sampling.")
    )
```

## Form Design Patterns

### Form Layout Guidelines

- Group related fields together
- Organize fields in a logical order (general to specific)
- Align labels and inputs consistently
- Use appropriate spacing between fields
- Clearly indicate required fields

### Input Validation

- Validate input as early as possible (during typing when appropriate)
- Display validation errors inline next to the relevant fields
- Prevent form submission with invalid data
- Provide clear error messages explaining how to correct problems
- Implement consistent visual indication of validation state

```python
# Example form validation
def validate_form(self):
    is_valid = True
    
    # Validate title field
    title = self.title_field.text()
    if not title:
        self.title_field.setError("Title is required")
        is_valid = False
    elif len(title) > 100:
        self.title_field.setError("Title cannot exceed 100 characters")
        is_valid = False
    else:
        self.title_field.setError("")
    
    # Validate content field
    content = self.content_field.toPlainText()
    if not content:
        self.content_field.setError("Content is required")
        is_valid = False
    else:
        self.content_field.setError("")
    
    return is_valid
```

## Testing and Quality Assurance

- Write unit tests for ViewModel and custom model classes
- Create UI automation tests for critical user workflows
- Test with different screen sizes and resolutions
- Verify keyboard navigation and screen reader accessibility
- Test with different visual themes and system settings

## Additional Resources

- [Qt Widget Gallery](https://doc.qt.io/qt-6/gallery.html)
- [Qt Style Sheets Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)
- [Qt Model/View Programming](https://doc.qt.io/qt-6/model-view-programming.html)
- [Qt Layouts](https://doc.qt.io/qt-6/layout.html)
- [Qt Internationalization](https://doc.qt.io/qt-6/internationalization.html)

## Conclusion

Following these UI standards ensures a consistent, accessible, and maintainable user interface for the Prometheus AI Prompt Generator. These guidelines should be used when designing new UI components or modifying existing ones.

Last updated: March 9, 2025 