"""
Settings Controller for the Prometheus AI Prompt Generator.

This module implements the SettingsController class which provides
a bridge between the UI and the application's settings persistence layer.
"""

import os
import json
from PyQt6.QtCore import QObject, QSettings, pyqtSignal, QStandardPaths

class SettingsController(QObject):
    """
    Controller for managing application settings.
    
    This class provides a unified interface for accessing and modifying
    application settings, abstracting the details of settings storage.
    It follows the MVC pattern, with this controller acting as the bridge
    between the settings dialog UI and the settings data model.
    """
    
    # Signal emitted when settings are changed and applied
    settingsChanged = pyqtSignal()
    
    def __init__(self):
        """Initialize the settings controller."""
        super().__init__()
        
        # Initialize QSettings
        self.settings = QSettings("PrometheusAI", "PromptGenerator")
        
        # Initialize cached API keys
        self._api_keys = {}
        self._load_api_keys()
        
        # Known API providers
        self._known_providers = [
            "OpenAI",
            "Google AI",
            "Anthropic",
            "Cohere",
            "Mistral AI",
            "Llama",
            "Azure OpenAI",
            "HuggingFace"
        ]
    
    def get_value(self, key, default=None):
        """
        Retrieve a setting value.
        
        Args:
            key: The settings key path
            default: Default value if the key does not exist
            
        Returns:
            The setting value or the default if not found
        """
        return self.settings.value(key, default)
    
    def set_value(self, key, value):
        """
        Set a setting value.
        
        Args:
            key: The settings key path
            value: The value to set
        """
        self.settings.setValue(key, value)
    
    def contains(self, key):
        """
        Check if a setting exists.
        
        Args:
            key: The settings key path
            
        Returns:
            True if the setting exists, False otherwise
        """
        return self.settings.contains(key)
    
    def remove(self, key):
        """
        Remove a setting.
        
        Args:
            key: The settings key path
        """
        self.settings.remove(key)
    
    def clear(self):
        """Clear all settings."""
        self.settings.clear()
    
    def sync(self):
        """Synchronize settings to disk."""
        self.settings.sync()
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        # Save API keys first, we don't want to lose those
        saved_api_keys = self._api_keys.copy()
        
        # Clear all settings
        self.settings.clear()
        
        # Restore API keys
        self._api_keys = saved_api_keys
        self._save_api_keys()
        
        # Apply default settings
        self._apply_default_settings()
        
        # Emit signal
        self.settingsChanged.emit()
    
    def _apply_default_settings(self):
        """Apply default settings."""
        # General defaults
        self.set_value("general/load_last_session", True)
        self.set_value("general/show_startup_tips", True)
        self.set_value("general/check_for_updates", True)
        self.set_value("general/default_save_location", 
                       QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
        self.set_value("general/autosave_enabled", True)
        self.set_value("general/create_backups", True)
        self.set_value("general/max_history_items", 100)
        self.set_value("general/clear_history_on_exit", False)
        
        # Appearance defaults
        self.set_value("appearance/theme", "Light")
        self.set_value("appearance/accent_color", "#0078D7")  # Windows blue
        self.set_value("appearance/interface_font", "Segoe UI")
        self.set_value("appearance/interface_font_size", 10)
        self.set_value("appearance/editor_font", "Consolas")
        self.set_value("appearance/editor_font_size", 11)
        self.set_value("appearance/font_smoothing", True)
        self.set_value("appearance/show_status_bar", True)
        self.set_value("appearance/show_toolbar", True)
        self.set_value("appearance/ui_density", "Normal")
        
        # Language defaults
        self.set_value("language/interface_language", "English")
        self.set_value("language/date_format", "System default")
        self.set_value("language/time_format", "System default")
        self.set_value("language/number_format", "System default")
        self.set_value("language/rtl_support", False)
        
        # API defaults
        if self._known_providers:
            self.set_value("api/default_provider", self._known_providers[0])
        self.set_value("api/usage_limit", 10.0)
        self.set_value("api/warn_on_limit", True)
        
        # Advanced defaults
        default_db_path = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation),
            "database")
        self.set_value("advanced/database_location", default_db_path)
        self.set_value("advanced/backup_frequency", "Weekly")
        self.set_value("advanced/log_level", "Info")
        self.set_value("advanced/log_retention", "30 days")
        self.set_value("advanced/performance_logging", False)
        self.set_value("advanced/cache_size_mb", 200)
        self.set_value("advanced/multithreading", True)
        self.set_value("advanced/prefetch_data", True)
    
    def apply_settings(self):
        """Apply settings changes and emit signal."""
        # Save settings to disk
        self.sync()
        
        # Emit signal that settings have changed
        self.settingsChanged.emit()
    
    def get_api_providers(self):
        """
        Get the list of API providers.
        
        Returns:
            List of known API provider names
        """
        return self._known_providers
    
    def get_api_keys(self):
        """
        Get the stored API keys.
        
        Returns:
            Dictionary of provider -> api key data
        """
        return self._api_keys
    
    def set_api_key(self, provider, key, verified=False):
        """
        Set an API key for a provider.
        
        Args:
            provider: The API provider name
            key: The API key value
            verified: Whether the key has been verified
        """
        self._api_keys[provider] = {
            "key": key,
            "verified": verified
        }
        self._save_api_keys()
    
    def remove_api_key(self, provider):
        """
        Remove an API key.
        
        Args:
            provider: The API provider name
            
        Returns:
            True if the key was removed, False if not found
        """
        if provider in self._api_keys:
            del self._api_keys[provider]
            self._save_api_keys()
            return True
        return False
    
    def verify_api_key(self, provider):
        """
        Verify an API key.
        
        This method would typically send a test request to the API
        to verify that the key is valid.
        
        Args:
            provider: The API provider name
            
        Returns:
            True if verification succeeded, False otherwise
        """
        # This is a placeholder for actual verification
        # In a real implementation, this would make an API call
        # to test the key's validity
        
        if provider in self._api_keys:
            self._api_keys[provider]["verified"] = True
            self._save_api_keys()
            return True
        return False
    
    def _load_api_keys(self):
        """Load API keys from settings."""
        api_keys_json = self.get_value("api/api_keys", "{}")
        try:
            self._api_keys = json.loads(api_keys_json)
        except json.JSONDecodeError:
            self._api_keys = {}
    
    def _save_api_keys(self):
        """Save API keys to settings."""
        api_keys_json = json.dumps(self._api_keys)
        self.set_value("api/api_keys", api_keys_json) 