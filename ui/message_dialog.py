from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings, Qt
from ui.designer.ui_message_dialog import Ui_MessageDialog


class MessageType:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class MessageDialog(QDialog):
    """
    A customizable message dialog for displaying information, warnings, errors, and questions.
    Supports customizable buttons, "don't show again" checkbox, and persistent settings.
    """

    def __init__(self, parent=None):
        super(MessageDialog, self).__init__(parent)
        self.ui = Ui_MessageDialog()
        self.ui.setupUi(self)
        
        self.settings = QSettings()
        self.settings_key = None
        self._configure_ui()
    
    def _configure_ui(self):
        """Configure default UI settings"""
        # Hide the don't show again checkbox by default
        self.ui.checkBox_dontShowAgain.setVisible(False)
    
    def set_message(self, title, message, message_type=MessageType.INFO, settings_key=None):
        """
        Set the message content and type
        
        Args:
            title (str): Dialog title
            message (str): Message content (can include HTML formatting)
            message_type (str): One of MessageType values
            settings_key (str): Settings key to remember "don't show again" preference
        
        Returns:
            self: For method chaining
        """
        self.setWindowTitle(title)
        self.ui.label_title.setText(title)
        self.ui.textBrowser_message.setHtml(message)
        
        # Set icon based on message type
        if message_type == MessageType.INFO:
            self.ui.label_icon.setPixmap(QIcon.fromTheme("dialog-information").pixmap(32, 32))
        elif message_type == MessageType.WARNING:
            self.ui.label_icon.setPixmap(QIcon.fromTheme("dialog-warning").pixmap(32, 32))
        elif message_type == MessageType.ERROR:
            self.ui.label_icon.setPixmap(QIcon.fromTheme("dialog-error").pixmap(32, 32))
        elif message_type == MessageType.QUESTION:
            self.ui.label_icon.setPixmap(QIcon.fromTheme("dialog-question").pixmap(32, 32))
        
        # Set the settings key if provided
        if settings_key:
            self.settings_key = settings_key
            self.ui.checkBox_dontShowAgain.setVisible(True)
        else:
            self.ui.checkBox_dontShowAgain.setVisible(False)
            
        return self
    
    def set_buttons(self, buttons):
        """
        Set the dialog buttons
        
        Args:
            buttons (QDialogButtonBox.StandardButtons): Standard buttons to display
        
        Returns:
            self: For method chaining
        """
        self.ui.buttonBox.setStandardButtons(buttons)
        return self
    
    def should_show(self):
        """
        Check if the dialog should be shown based on saved preferences
        
        Returns:
            bool: True if the dialog should be shown, False otherwise
        """
        if not self.settings_key:
            return True
            
        return not self.settings.value(f"MessageDialog/{self.settings_key}/DontShow", False, bool)
    
    def exec(self):
        """
        Show the dialog and return the result
        
        Returns:
            int: Dialog result code
        """
        # Check if we should show the dialog
        if not self.should_show():
            # Return OK by default when dialog is suppressed
            return QDialog.Accepted
            
        result = super().exec()
        
        # Save the "don't show again" preference if checked
        if self.settings_key and self.ui.checkBox_dontShowAgain.isChecked():
            self.settings.setValue(f"MessageDialog/{self.settings_key}/DontShow", True)
            
        return result
    
    @staticmethod
    def show_info(parent, title, message, settings_key=None):
        """
        Static convenience method to show an info dialog
        
        Returns:
            int: Dialog result code
        """
        dialog = MessageDialog(parent)
        dialog.set_message(title, message, MessageType.INFO, settings_key)
        return dialog.exec()
    
    @staticmethod
    def show_warning(parent, title, message, settings_key=None):
        """
        Static convenience method to show a warning dialog
        
        Returns:
            int: Dialog result code
        """
        dialog = MessageDialog(parent)
        dialog.set_message(title, message, MessageType.WARNING, settings_key)
        return dialog.exec()
    
    @staticmethod
    def show_error(parent, title, message, settings_key=None):
        """
        Static convenience method to show an error dialog
        
        Returns:
            int: Dialog result code
        """
        dialog = MessageDialog(parent)
        dialog.set_message(title, message, MessageType.ERROR, settings_key)
        return dialog.exec()
    
    @staticmethod
    def show_question(parent, title, message, settings_key=None):
        """
        Static convenience method to show a question dialog
        
        Returns:
            int: Dialog result code (QDialog.Accepted or QDialog.Rejected)
        """
        dialog = MessageDialog(parent)
        dialog.set_message(title, message, MessageType.QUESTION, settings_key)
        dialog.set_buttons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        return dialog.exec() 