"""
Settings Dialog for the Prometheus AI Prompt Generator.

This module contains the SettingsDialog class which provides
a UI for configuring application settings.
"""

import os
from PyQt6.QtWidgets import QDialog, QColorDialog, QFileDialog, QMessageBox
from PyQt6.QtCore import QSettings, pyqtSignal, Qt
from PyQt6.QtGui import QColor

from ui.designer.ui_settings_dialog import Ui_SettingsDialog
from prometheus_prompt_generator.domain.controllers.settings_controller import SettingsController


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring the application.
    
    This dialog provides a tabbed interface for configuring various aspects
    of the application, including general settings, appearance, API providers,
    language settings, and advanced options.
    
    The dialog uses the SettingsController to interact with the application's
    settings storage.
    """
    
    # Signal emitted when settings are changed and applied
    settingsChanged = pyqtSignal()
    
    def __init__(self, parent=None, settings_controller=None):
        """
        Initialize the settings dialog.
        
        Args:
            parent: The parent widget
            settings_controller: Controller for managing settings
        """
        super().__init__(parent)
        
        # Set up the UI
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        
        # Store reference to the settings controller
        self.settings_controller = settings_controller or SettingsController()
        
        # Set up connections
        self._setup_connections()
        
        # Load current settings
        self._load_settings()
        
        # Track whether settings have changed
        self.settings_changed = False
        
        # Initialize API provider combobox
        self._populate_api_providers()
        
        # Set window properties
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumSize(600, 500)
        
    def _setup_connections(self):
        """Set up signal-slot connections."""
        # General tab connections
        self.ui.browseSaveLocationButton.clicked.connect(self._browse_save_location)
        
        # Appearance tab connections
        self.ui.accentColorButton.clicked.connect(self._choose_accent_color)
        
        # API Providers tab connections
        self.ui.addApiKeyButton.clicked.connect(self._add_api_key)
        self.ui.editApiKeyButton.clicked.connect(self._edit_api_key)
        self.ui.removeApiKeyButton.clicked.connect(self._remove_api_key)
        self.ui.verifyApiKeyButton.clicked.connect(self._verify_api_key)
        
        # Advanced tab connections
        self.ui.browseDatabaseButton.clicked.connect(self._browse_database_location)
        self.ui.backupDatabaseButton.clicked.connect(self._backup_database)
        self.ui.restoreDatabaseButton.clicked.connect(self._restore_database)
        self.ui.compactDatabaseButton.clicked.connect(self._compact_database)
        
        # Dialog button connections
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Reset).clicked.connect(self._reset_settings)
        
        # Connect accepted/rejected signals
        self.accepted.connect(self._apply_settings)
        
    def _load_settings(self):
        """Load current settings from the controller into the UI."""
        # General tab
        self.ui.loadLastSessionCheckBox.setChecked(
            self.settings_controller.get_value("general/load_last_session", True))
        self.ui.showStartupTipsCheckBox.setChecked(
            self.settings_controller.get_value("general/show_startup_tips", True))
        self.ui.checkForUpdatesCheckBox.setChecked(
            self.settings_controller.get_value("general/check_for_updates", True))
        self.ui.defaultSaveLocationEdit.setText(
            self.settings_controller.get_value("general/default_save_location", ""))
        self.ui.autosaveCheckBox.setChecked(
            self.settings_controller.get_value("general/autosave_enabled", True))
        self.ui.createBackupsCheckBox.setChecked(
            self.settings_controller.get_value("general/create_backups", True))
        self.ui.maxHistoryItemsSpinBox.setValue(
            self.settings_controller.get_value("general/max_history_items", 100))
        self.ui.clearHistoryOnExitCheckBox.setChecked(
            self.settings_controller.get_value("general/clear_history_on_exit", False))
        
        # Appearance tab
        theme_index = self.ui.themeComboBox.findText(
            self.settings_controller.get_value("appearance/theme", "Light"))
        self.ui.themeComboBox.setCurrentIndex(max(0, theme_index))
        
        accent_color = QColor(self.settings_controller.get_value("appearance/accent_color", "#0078D7"))
        self._update_accent_color_button(accent_color)
        
        interface_font = self.settings_controller.get_value("appearance/interface_font", self.font().family())
        interface_font_size = self.settings_controller.get_value("appearance/interface_font_size", 10)
        self.ui.interfaceFontComboBox.setCurrentFont(interface_font)
        self.ui.interfaceFontSizeSpinBox.setValue(interface_font_size)
        
        editor_font = self.settings_controller.get_value("appearance/editor_font", "Consolas")
        editor_font_size = self.settings_controller.get_value("appearance/editor_font_size", 11)
        self.ui.editorFontComboBox.setCurrentFont(editor_font)
        self.ui.editorFontSizeSpinBox.setValue(editor_font_size)
        
        self.ui.enableFontSmoothingCheckBox.setChecked(
            self.settings_controller.get_value("appearance/font_smoothing", True))
        
        self.ui.showStatusBarCheckBox.setChecked(
            self.settings_controller.get_value("appearance/show_status_bar", True))
        self.ui.showToolbarCheckBox.setChecked(
            self.settings_controller.get_value("appearance/show_toolbar", True))
        
        ui_density_index = self.ui.uiDensityComboBox.findText(
            self.settings_controller.get_value("appearance/ui_density", "Normal"))
        self.ui.uiDensityComboBox.setCurrentIndex(max(1, ui_density_index))
        
        # Language tab
        language_index = self.ui.languageComboBox.findText(
            self.settings_controller.get_value("language/interface_language", "English"))
        self.ui.languageComboBox.setCurrentIndex(max(0, language_index))
        
        date_format_index = self.ui.dateFormatComboBox.findText(
            self.settings_controller.get_value("language/date_format", "System default"))
        self.ui.dateFormatComboBox.setCurrentIndex(max(0, date_format_index))
        
        time_format_index = self.ui.timeFormatComboBox.findText(
            self.settings_controller.get_value("language/time_format", "System default"))
        self.ui.timeFormatComboBox.setCurrentIndex(max(0, time_format_index))
        
        number_format_index = self.ui.numberFormatComboBox.findText(
            self.settings_controller.get_value("language/number_format", "System default"))
        self.ui.numberFormatComboBox.setCurrentIndex(max(0, number_format_index))
        
        self.ui.rtlSupportCheckBox.setChecked(
            self.settings_controller.get_value("language/rtl_support", False))
        
        # Advanced tab
        self.ui.databaseLocationLineEdit.setText(
            self.settings_controller.get_value("advanced/database_location", ""))
        
        backup_frequency_index = self.ui.autoBackupComboBox.findText(
            self.settings_controller.get_value("advanced/backup_frequency", "Weekly"))
        self.ui.autoBackupComboBox.setCurrentIndex(max(1, backup_frequency_index))
        
        log_level_index = self.ui.logLevelComboBox.findText(
            self.settings_controller.get_value("advanced/log_level", "Info"))
        self.ui.logLevelComboBox.setCurrentIndex(max(1, log_level_index))
        
        log_retention_index = self.ui.logRetentionComboBox.findText(
            self.settings_controller.get_value("advanced/log_retention", "30 days"))
        self.ui.logRetentionComboBox.setCurrentIndex(max(2, log_retention_index))
        
        self.ui.enablePerformanceLoggingCheckBox.setChecked(
            self.settings_controller.get_value("advanced/performance_logging", False))
        
        self.ui.cacheSizeSpinBox.setValue(
            self.settings_controller.get_value("advanced/cache_size_mb", 200))
        
        self.ui.enableMultithreadingCheckBox.setChecked(
            self.settings_controller.get_value("advanced/multithreading", True))
        
        self.ui.prefetchDataCheckBox.setChecked(
            self.settings_controller.get_value("advanced/prefetch_data", True))
        
        # API keys are loaded in _populate_api_providers
        # Populate the API keys table
        self._load_api_keys()
        
    def _apply_settings(self):
        """Save settings from the UI to the controller."""
        # General tab
        self.settings_controller.set_value(
            "general/load_last_session", self.ui.loadLastSessionCheckBox.isChecked())
        self.settings_controller.set_value(
            "general/show_startup_tips", self.ui.showStartupTipsCheckBox.isChecked())
        self.settings_controller.set_value(
            "general/check_for_updates", self.ui.checkForUpdatesCheckBox.isChecked())
        self.settings_controller.set_value(
            "general/default_save_location", self.ui.defaultSaveLocationEdit.text())
        self.settings_controller.set_value(
            "general/autosave_enabled", self.ui.autosaveCheckBox.isChecked())
        self.settings_controller.set_value(
            "general/create_backups", self.ui.createBackupsCheckBox.isChecked())
        self.settings_controller.set_value(
            "general/max_history_items", self.ui.maxHistoryItemsSpinBox.value())
        self.settings_controller.set_value(
            "general/clear_history_on_exit", self.ui.clearHistoryOnExitCheckBox.isChecked())
        
        # Appearance tab
        self.settings_controller.set_value(
            "appearance/theme", self.ui.themeComboBox.currentText())
        self.settings_controller.set_value(
            "appearance/accent_color", self._get_current_accent_color().name())
        self.settings_controller.set_value(
            "appearance/interface_font", self.ui.interfaceFontComboBox.currentFont().family())
        self.settings_controller.set_value(
            "appearance/interface_font_size", self.ui.interfaceFontSizeSpinBox.value())
        self.settings_controller.set_value(
            "appearance/editor_font", self.ui.editorFontComboBox.currentFont().family())
        self.settings_controller.set_value(
            "appearance/editor_font_size", self.ui.editorFontSizeSpinBox.value())
        self.settings_controller.set_value(
            "appearance/font_smoothing", self.ui.enableFontSmoothingCheckBox.isChecked())
        self.settings_controller.set_value(
            "appearance/show_status_bar", self.ui.showStatusBarCheckBox.isChecked())
        self.settings_controller.set_value(
            "appearance/show_toolbar", self.ui.showToolbarCheckBox.isChecked())
        self.settings_controller.set_value(
            "appearance/ui_density", self.ui.uiDensityComboBox.currentText())
        
        # Language tab
        self.settings_controller.set_value(
            "language/interface_language", self.ui.languageComboBox.currentText())
        self.settings_controller.set_value(
            "language/date_format", self.ui.dateFormatComboBox.currentText())
        self.settings_controller.set_value(
            "language/time_format", self.ui.timeFormatComboBox.currentText())
        self.settings_controller.set_value(
            "language/number_format", self.ui.numberFormatComboBox.currentText())
        self.settings_controller.set_value(
            "language/rtl_support", self.ui.rtlSupportCheckBox.isChecked())
        
        # API Providers tab
        if self.ui.defaultProviderComboBox.currentText():
            self.settings_controller.set_value(
                "api/default_provider", self.ui.defaultProviderComboBox.currentText())
        self.settings_controller.set_value(
            "api/usage_limit", self.ui.usageLimitSpinBox.value())
        self.settings_controller.set_value(
            "api/warn_on_limit", self.ui.warnOnLimitCheckBox.isChecked())
        
        # Save API keys (handled separately by SettingsController)
        self._save_api_keys()
        
        # Advanced tab
        self.settings_controller.set_value(
            "advanced/database_location", self.ui.databaseLocationLineEdit.text())
        self.settings_controller.set_value(
            "advanced/backup_frequency", self.ui.autoBackupComboBox.currentText())
        self.settings_controller.set_value(
            "advanced/log_level", self.ui.logLevelComboBox.currentText())
        self.settings_controller.set_value(
            "advanced/log_retention", self.ui.logRetentionComboBox.currentText())
        self.settings_controller.set_value(
            "advanced/performance_logging", self.ui.enablePerformanceLoggingCheckBox.isChecked())
        self.settings_controller.set_value(
            "advanced/cache_size_mb", self.ui.cacheSizeSpinBox.value())
        self.settings_controller.set_value(
            "advanced/multithreading", self.ui.enableMultithreadingCheckBox.isChecked())
        self.settings_controller.set_value(
            "advanced/prefetch_data", self.ui.prefetchDataCheckBox.isChecked())
        
        # Apply settings
        self.settings_controller.apply_settings()
        
        # Emit signal
        self.settingsChanged.emit()
        
        # Reset the changed flag
        self.settings_changed = False
        
    def _reset_settings(self):
        """Reset settings to their default values."""
        # Confirm with the user
        result = QMessageBox.question(
            self,
            self.tr("Reset Settings"),
            self.tr("Are you sure you want to reset all settings to their default values?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Reset settings in the controller
            self.settings_controller.reset_to_defaults()
            
            # Reload settings into the UI
            self._load_settings()
            
            # Notify the user
            QMessageBox.information(
                self,
                self.tr("Settings Reset"),
                self.tr("All settings have been reset to their default values.")
            )
            
            # Mark settings as changed
            self.settings_changed = True
    
    def _browse_save_location(self):
        """Open a file dialog to browse for the default save location."""
        current_dir = self.ui.defaultSaveLocationEdit.text()
        if not current_dir or not os.path.isdir(current_dir):
            current_dir = os.path.expanduser("~/Documents")
            
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Default Save Location"),
            current_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if directory:
            self.ui.defaultSaveLocationEdit.setText(directory)
            self.settings_changed = True
    
    def _browse_database_location(self):
        """Open a file dialog to browse for the database location."""
        current_location = self.ui.databaseLocationLineEdit.text()
        if not current_location:
            current_location = os.path.expanduser("~")
            
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Database Location"),
            current_location,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if directory:
            self.ui.databaseLocationLineEdit.setText(directory)
            self.settings_changed = True
    
    def _choose_accent_color(self):
        """Open a color dialog to choose the accent color."""
        current_color = self._get_current_accent_color()
        
        color = QColorDialog.getColor(
            current_color,
            self,
            self.tr("Select Accent Color"),
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        
        if color.isValid():
            self._update_accent_color_button(color)
            self.settings_changed = True
    
    def _get_current_accent_color(self):
        """Get the current accent color from the button."""
        # The color is stored in the button's property
        color_property = self.ui.accentColorButton.property("color")
        
        if color_property:
            return QColor(color_property)
        else:
            # Default color
            return QColor("#0078D7")
    
    def _update_accent_color_button(self, color):
        """Update the accent color button with the selected color."""
        # Store the color as a property
        self.ui.accentColorButton.setProperty("color", color.name())
        
        # Set the button's background to the selected color
        self.ui.accentColorButton.setStyleSheet(
            f"QPushButton {{ background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'}; }}"
        )
    
    def _populate_api_providers(self):
        """Populate the API providers dropdown."""
        providers = self.settings_controller.get_api_providers()
        
        self.ui.defaultProviderComboBox.clear()
        self.ui.defaultProviderComboBox.addItems(providers)
        
        default_provider = self.settings_controller.get_value("api/default_provider", "")
        if default_provider:
            index = self.ui.defaultProviderComboBox.findText(default_provider)
            if index >= 0:
                self.ui.defaultProviderComboBox.setCurrentIndex(index)
    
    def _load_api_keys(self):
        """Load API keys into the table."""
        api_keys = self.settings_controller.get_api_keys()
        
        # Clear the table
        self.ui.apiKeyTable.setRowCount(0)
        
        # Add each API key to the table
        for provider, key_data in api_keys.items():
            row = self.ui.apiKeyTable.rowCount()
            self.ui.apiKeyTable.insertRow(row)
            
            # Set provider name
            self.ui.apiKeyTable.setItem(row, 0, QTableWidgetItem(provider))
            
            # Set masked API key
            masked_key = "•" * 8 + key_data.get("key", "")[-4:] if key_data.get("key") else ""
            self.ui.apiKeyTable.setItem(row, 1, QTableWidgetItem(masked_key))
            
            # Set status
            status = key_data.get("verified", False)
            status_text = self.tr("Verified") if status else self.tr("Not verified")
            self.ui.apiKeyTable.setItem(row, 2, QTableWidgetItem(status_text))
    
    def _save_api_keys(self):
        """Save API keys from the controller."""
        # API keys are managed by the SettingsController
        # This function is a placeholder for additional processing if needed
        pass
    
    def _add_api_key(self):
        """Add a new API key."""
        # This would typically open a dialog to add a new API key
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Add API Key"),
            self.tr("API key management functionality will be implemented in a future update.")
        )
    
    def _edit_api_key(self):
        """Edit the selected API key."""
        # Get the selected row
        selected_rows = self.ui.apiKeyTable.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                self.tr("Edit API Key"),
                self.tr("Please select an API key to edit.")
            )
            return
            
        # This would typically open a dialog to edit the API key
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Edit API Key"),
            self.tr("API key management functionality will be implemented in a future update.")
        )
    
    def _remove_api_key(self):
        """Remove the selected API key."""
        # Get the selected row
        selected_rows = self.ui.apiKeyTable.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                self.tr("Remove API Key"),
                self.tr("Please select an API key to remove.")
            )
            return
            
        # This would typically remove the selected API key
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Remove API Key"),
            self.tr("API key management functionality will be implemented in a future update.")
        )
    
    def _verify_api_key(self):
        """Verify the selected API key."""
        # Get the selected row
        selected_rows = self.ui.apiKeyTable.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                self.tr("Verify API Key"),
                self.tr("Please select an API key to verify.")
            )
            return
            
        # This would typically verify the selected API key
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Verify API Key"),
            self.tr("API key verification functionality will be implemented in a future update.")
        )
    
    def _backup_database(self):
        """Backup the database."""
        # This would typically backup the database
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Backup Database"),
            self.tr("Database backup functionality will be implemented in a future update.")
        )
    
    def _restore_database(self):
        """Restore the database from a backup."""
        # This would typically restore the database from a backup
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Restore Database"),
            self.tr("Database restore functionality will be implemented in a future update.")
        )
    
    def _compact_database(self):
        """Compact the database."""
        # This would typically compact the database
        # For now, we'll just show a message
        QMessageBox.information(
            self,
            self.tr("Compact Database"),
            self.tr("Database compaction functionality will be implemented in a future update.")
        ) 