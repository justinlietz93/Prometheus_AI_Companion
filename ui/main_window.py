from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QSettings, Slot, Qt
from ui.designer.ui_main_window import Ui_MainWindow
from ui.message_dialog import MessageDialog
from ui.help_dialog import HelpDialog


class MainWindow(QMainWindow):
    """
    Main application window with connections to controllers using the MVC pattern.
    """
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize settings
        self.settings = QSettings()
        
        # Controllers will be initialized by the application
        self.prompt_controller = None
        self.tag_controller = None
        self.filter_controller = None
        self.generation_controller = None
        self.scoring_controller = None
        self.usage_controller = None
        self.benchmark_controller = None
        self.settings_controller = None
        
        # Configure UI
        self._setup_ui()
        self._connect_signals()
        
        # Restore window state
        self._restore_window_state()
    
    def set_controllers(self, controllers):
        """
        Set the controllers needed for the UI
        
        Args:
            controllers (dict): Dictionary of controller instances
        """
        self.prompt_controller = controllers.get('prompt')
        self.tag_controller = controllers.get('tag')
        self.filter_controller = controllers.get('filter')
        self.generation_controller = controllers.get('generation')
        self.scoring_controller = controllers.get('scoring')
        self.usage_controller = controllers.get('usage')
        self.benchmark_controller = controllers.get('benchmark')
        self.settings_controller = controllers.get('settings')
        
        # Connect models to views
        self._connect_models()
    
    def _setup_ui(self):
        """Configure initial UI state"""
        # Update status bar
        self.ui.statusbar.showMessage("Ready")
        
        # Setup prompt list view
        
        # Setup tag list view
        
        # Setup category tree view
    
    def _connect_signals(self):
        """Connect UI signals to slots"""
        # File menu
        self.ui.actionNew_Prompt.triggered.connect(self._on_new_prompt)
        self.ui.actionOpen_Prompt.triggered.connect(self._on_open_prompt)
        self.ui.actionSave_Prompt.triggered.connect(self._on_save_prompt)
        self.ui.actionSave_As.triggered.connect(self._on_save_prompt_as)
        self.ui.actionImport.triggered.connect(self._on_import)
        self.ui.actionExport.triggered.connect(self._on_export)
        self.ui.actionExit.triggered.connect(self.close)
        
        # Edit menu
        self.ui.actionUndo.triggered.connect(self._on_undo)
        self.ui.actionRedo.triggered.connect(self._on_redo)
        self.ui.actionCut.triggered.connect(self._on_cut)
        self.ui.actionCopy.triggered.connect(self._on_copy)
        self.ui.actionPaste.triggered.connect(self._on_paste)
        self.ui.actionFind.triggered.connect(self._on_find)
        self.ui.actionSettings.triggered.connect(self._on_settings)
        
        # View menu
        self.ui.actionPrompt_Library.triggered.connect(self._on_toggle_prompt_library)
        self.ui.actionPrompt_Editor.triggered.connect(self._on_toggle_prompt_editor)
        self.ui.actionAnalytics_Dashboard.triggered.connect(self._on_toggle_analytics_dashboard)
        self.ui.actionBenchmarking.triggered.connect(self._on_toggle_benchmarking)
        
        # Tools menu
        self.ui.actionGenerate_Prompt.triggered.connect(self._on_generate_prompt)
        self.ui.actionAnalyze_Prompt.triggered.connect(self._on_analyze_prompt)
        self.ui.actionBenchmark_Models.triggered.connect(self._on_benchmark_models)
        
        # Help menu
        self.ui.actionHelp_Contents.triggered.connect(self._on_help_contents)
        self.ui.actionAbout.triggered.connect(self._on_about)
        
        # Toolbar actions
        
        # List view signals
    
    def _connect_models(self):
        """Connect models to views using MVC pattern"""
        if not self.prompt_controller:
            return
        
        # Connect prompt model to views
        
        # Connect tag model
        
        # Connect filter model
    
    def _restore_window_state(self):
        """Restore window position, size and state from settings"""
        geometry = self.settings.value("MainWindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("MainWindow/state")
        if state:
            self.restoreState(state)
        
        # Restore dock widget visibility
        for dock_name in ["promptLibrary", "promptEditor", "analyticsDashboard", "benchmarking"]:
            dock_widget = getattr(self.ui, f"dock{dock_name.title()}")
            visible = self.settings.value(f"MainWindow/dock{dock_name.title()}Visible", True, bool)
            dock_widget.setVisible(visible)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self.settings.setValue("MainWindow/geometry", self.saveGeometry())
        self.settings.setValue("MainWindow/state", self.saveState())
        
        # Save dock widget visibility
        for dock_name in ["promptLibrary", "promptEditor", "analyticsDashboard", "benchmarking"]:
            dock_widget = getattr(self.ui, f"dock{dock_name.title()}")
            self.settings.setValue(f"MainWindow/dock{dock_name.title()}Visible", dock_widget.isVisible())
        
        # Accept the close event
        event.accept()
    
    # File menu slots
    @Slot()
    def _on_new_prompt(self):
        """Create a new prompt"""
        if self.prompt_controller:
            self.prompt_controller.create_new_prompt()
    
    @Slot()
    def _on_open_prompt(self):
        """Open a prompt from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Prompt",
            "",
            "Prompt Files (*.json *.txt);;All Files (*)"
        )
        
        if file_path and self.prompt_controller:
            try:
                self.prompt_controller.load_prompt_from_file(file_path)
            except Exception as e:
                MessageDialog.show_error(self, "Error Opening Prompt", f"Could not open prompt file: {str(e)}")
    
    @Slot()
    def _on_save_prompt(self):
        """Save the current prompt"""
        if self.prompt_controller:
            try:
                self.prompt_controller.save_current_prompt()
            except Exception as e:
                MessageDialog.show_error(self, "Error Saving Prompt", f"Could not save prompt: {str(e)}")
    
    @Slot()
    def _on_save_prompt_as(self):
        """Save the current prompt to a new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Prompt As",
            "",
            "Prompt Files (*.json *.txt);;All Files (*)"
        )
        
        if file_path and self.prompt_controller:
            try:
                self.prompt_controller.save_current_prompt_as(file_path)
            except Exception as e:
                MessageDialog.show_error(self, "Error Saving Prompt", f"Could not save prompt: {str(e)}")
    
    @Slot()
    def _on_import(self):
        """Import prompts"""
        pass  # To be implemented
    
    @Slot()
    def _on_export(self):
        """Export prompts"""
        pass  # To be implemented
    
    # Edit menu slots
    @Slot()
    def _on_undo(self):
        """Undo the last action"""
        focus_widget = self.focusWidget()
        if hasattr(focus_widget, 'undo'):
            focus_widget.undo()
    
    @Slot()
    def _on_redo(self):
        """Redo the previously undone action"""
        focus_widget = self.focusWidget()
        if hasattr(focus_widget, 'redo'):
            focus_widget.redo()
    
    @Slot()
    def _on_cut(self):
        """Cut the selected text"""
        focus_widget = self.focusWidget()
        if hasattr(focus_widget, 'cut'):
            focus_widget.cut()
    
    @Slot()
    def _on_copy(self):
        """Copy the selected text"""
        focus_widget = self.focusWidget()
        if hasattr(focus_widget, 'copy'):
            focus_widget.copy()
    
    @Slot()
    def _on_paste(self):
        """Paste text from the clipboard"""
        focus_widget = self.focusWidget()
        if hasattr(focus_widget, 'paste'):
            focus_widget.paste()
    
    @Slot()
    def _on_find(self):
        """Find text in the current view"""
        pass  # To be implemented
    
    @Slot()
    def _on_settings(self):
        """Open settings dialog"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, self.settings_controller)
        dialog.exec()
    
    # View menu slots
    @Slot()
    def _on_toggle_prompt_library(self):
        """Toggle prompt library dock visibility"""
        self.ui.dockPromptLibrary.setVisible(not self.ui.dockPromptLibrary.isVisible())
    
    @Slot()
    def _on_toggle_prompt_editor(self):
        """Toggle prompt editor dock visibility"""
        self.ui.dockPromptEditor.setVisible(not self.ui.dockPromptEditor.isVisible())
    
    @Slot()
    def _on_toggle_analytics_dashboard(self):
        """Toggle analytics dashboard dock visibility"""
        self.ui.dockAnalyticsDashboard.setVisible(not self.ui.dockAnalyticsDashboard.isVisible())
    
    @Slot()
    def _on_toggle_benchmarking(self):
        """Toggle benchmarking dock visibility"""
        self.ui.dockBenchmarking.setVisible(not self.ui.dockBenchmarking.isVisible())
    
    # Tools menu slots
    @Slot()
    def _on_generate_prompt(self):
        """Generate a prompt"""
        pass  # To be implemented
    
    @Slot()
    def _on_analyze_prompt(self):
        """Analyze a prompt"""
        pass  # To be implemented
    
    @Slot()
    def _on_benchmark_models(self):
        """Run a benchmark on models"""
        pass  # To be implemented
    
    # Help menu slots
    @Slot()
    def _on_help_contents(self):
        """Show help contents"""
        HelpDialog.show_help(self)
    
    @Slot()
    def _on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Prometheus AI Prompt Generator",
            "<h3>Prometheus AI Prompt Generator</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A professional tool for creating, managing, and analyzing AI prompts.</p>"
            "<p>&copy; 2025 Prometheus AI Team</p>"
        ) 