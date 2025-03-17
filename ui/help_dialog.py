from PySide6.QtWidgets import QDialog, QTreeWidgetItem
from PySide6.QtCore import Qt, QUrl, QStandardPaths, QDir, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem
from ui.designer.ui_help_dialog import Ui_HelpDialog
import os
import re


class HelpDialog(QDialog):
    """
    A help dialog with navigation, search, and content display.
    """
    
    def __init__(self, parent=None, help_dir=None):
        super(HelpDialog, self).__init__(parent)
        self.ui = Ui_HelpDialog()
        self.ui.setupUi(self)
        
        # Initialize variables
        self.help_dir = help_dir or self._get_default_help_dir()
        self.history = []
        self.history_position = -1
        self.contents_model = QStandardItemModel(self)
        
        # Configure UI
        self._setup_ui()
        self._connect_signals()
        
        # Load contents
        self._load_contents()
        self._load_home_page()
    
    def _setup_ui(self):
        """Set up initial UI configuration"""
        # Set up tree view
        self.ui.treeView_contents.setModel(self.contents_model)
        self.contents_model.setHorizontalHeaderLabels(["Topics"])
        
        # Disable navigation buttons initially
        self.ui.pushButton_back.setEnabled(False)
        self.ui.pushButton_forward.setEnabled(False)
    
    def _connect_signals(self):
        """Connect UI signals to slots"""
        # Connect navigation buttons
        self.ui.pushButton_back.clicked.connect(self._navigate_back)
        self.ui.pushButton_forward.clicked.connect(self._navigate_forward)
        self.ui.pushButton_home.clicked.connect(self._load_home_page)
        
        # Connect tree view selection
        self.ui.treeView_contents.clicked.connect(self._on_topic_clicked)
        
        # Connect search
        self.ui.lineEdit_search.textChanged.connect(self._on_search_text_changed)
        self.ui.lineEdit_search.returnPressed.connect(self._on_search_submitted)
    
    def _get_default_help_dir(self):
        """Get the default help directory"""
        app_data_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return os.path.join(app_data_path, "help")
    
    def _load_contents(self):
        """Load the help contents tree"""
        # Clear existing items
        self.contents_model.clear()
        
        # Create root item
        root_item = QStandardItem("Prometheus AI Prompt Generator")
        self.contents_model.appendRow(root_item)
        
        # Add categories
        categories = [
            ("Getting Started", ["Installation", "Basic Concepts", "Quick Start Guide"]),
            ("Creating Prompts", ["Prompt Editor", "Templates", "Variables", "Categories"]),
            ("Managing Prompts", ["Organizing", "Tagging", "Searching", "Import/Export"]),
            ("Analytics", ["Scoring", "Usage Tracking", "Performance Metrics"]),
            ("Benchmarking", ["Running Benchmarks", "Comparing Models", "Analyzing Results"]),
            ("Settings", ["General", "Appearance", "LLM Providers", "API Keys"]),
            ("Advanced Topics", ["Custom Templates", "Scripting", "Integration"])
        ]
        
        # Add categories and topics to the tree
        for category, topics in categories:
            category_item = QStandardItem(category)
            root_item.appendRow(category_item)
            
            for topic in topics:
                topic_item = QStandardItem(topic)
                topic_item.setData(f"{category.lower().replace(' ', '_')}/{topic.lower().replace(' ', '_')}.html", Qt.UserRole)
                category_item.appendRow(topic_item)
        
        # Expand the tree
        self.ui.treeView_contents.expandAll()
    
    def _load_home_page(self):
        """Load the home page"""
        self._navigate_to_page("index.html")
    
    def _navigate_to_page(self, page):
        """Navigate to a specific page"""
        # If we're not at the end of the history, truncate it
        if self.history_position < len(self.history) - 1:
            self.history = self.history[:self.history_position + 1]
        
        # Add the page to history
        self.history.append(page)
        self.history_position = len(self.history) - 1
        
        # Update navigation button states
        self._update_navigation_buttons()
        
        # Load the page
        file_path = os.path.join(self.help_dir, page)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.ui.textBrowser_helpContent.setHtml(content)
        else:
            self.ui.textBrowser_helpContent.setHtml(f"<h1>Page Not Found</h1><p>The help page '{page}' could not be found.</p>")
    
    def _navigate_back(self):
        """Navigate back in history"""
        if self.history_position > 0:
            self.history_position -= 1
            page = self.history[self.history_position]
            
            # Load the page without modifying history
            file_path = os.path.join(self.help_dir, page)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.ui.textBrowser_helpContent.setHtml(content)
            
            # Update navigation button states
            self._update_navigation_buttons()
    
    def _navigate_forward(self):
        """Navigate forward in history"""
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            page = self.history[self.history_position]
            
            # Load the page without modifying history
            file_path = os.path.join(self.help_dir, page)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.ui.textBrowser_helpContent.setHtml(content)
            
            # Update navigation button states
            self._update_navigation_buttons()
    
    def _update_navigation_buttons(self):
        """Update the enabled state of navigation buttons"""
        self.ui.pushButton_back.setEnabled(self.history_position > 0)
        self.ui.pushButton_forward.setEnabled(self.history_position < len(self.history) - 1)
    
    @Slot()
    def _on_topic_clicked(self, index):
        """Handle topic selection in the tree view"""
        item = self.contents_model.itemFromIndex(index)
        page_path = item.data(Qt.UserRole)
        
        if page_path:
            self._navigate_to_page(page_path)
    
    @Slot(str)
    def _on_search_text_changed(self, text):
        """Handle search text changes"""
        # If search box is cleared, reset the tree
        if not text:
            self._load_contents()
            return
    
    @Slot()
    def _on_search_submitted(self):
        """Handle search submission"""
        search_text = self.ui.lineEdit_search.text()
        if not search_text:
            return
        
        # Perform search across help files
        results = self._search_help_content(search_text)
        
        # Display results
        self._display_search_results(search_text, results)
    
    def _search_help_content(self, search_text):
        """
        Search through help content for matching text
        
        Args:
            search_text (str): Text to search for
            
        Returns:
            list: List of (file_path, title, excerpt) tuples with search results
        """
        results = []
        search_pattern = re.compile(re.escape(search_text), re.IGNORECASE)
        
        # Walk through help directory
        for root, _, files in os.walk(self.help_dir):
            for file in files:
                if file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.help_dir)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Extract title
                            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                            title = title_match.group(1) if title_match else rel_path
                            
                            # Check for matches
                            if search_pattern.search(content):
                                # Extract a relevant excerpt
                                plain_text = re.sub(r'<[^>]+>', ' ', content)
                                match = search_pattern.search(plain_text)
                                if match:
                                    pos = match.start()
                                    start = max(0, pos - 50)
                                    end = min(len(plain_text), pos + 50)
                                    excerpt = plain_text[start:end].strip()
                                    excerpt = f"...{excerpt}..." if start > 0 or end < len(plain_text) else excerpt
                                    
                                    results.append((rel_path, title, excerpt))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return results
    
    def _display_search_results(self, search_text, results):
        """
        Display search results in the tree view
        
        Args:
            search_text (str): The search text
            results (list): List of (file_path, title, excerpt) tuples
        """
        # Clear existing items
        self.contents_model.clear()
        
        # Create root item for search results
        root_item = QStandardItem(f"Search Results for '{search_text}'")
        self.contents_model.appendRow(root_item)
        
        # Add results
        for file_path, title, excerpt in results:
            # Create item for this result
            result_item = QStandardItem(title)
            result_item.setData(file_path, Qt.UserRole)
            
            # Add excerpt as child item
            excerpt_item = QStandardItem(excerpt)
            excerpt_item.setData(file_path, Qt.UserRole)
            
            # Add to tree
            root_item.appendRow(result_item)
            result_item.appendRow(excerpt_item)
        
        # Expand all items
        self.ui.treeView_contents.expandAll()
        
        # Show message if no results
        if not results:
            no_results_item = QStandardItem("No results found")
            root_item.appendRow(no_results_item)
    
    @staticmethod
    def show_help(parent=None, topic=None):
        """
        Static convenience method to show the help dialog
        
        Args:
            parent: Parent widget
            topic: Optional topic to navigate to
            
        Returns:
            int: Dialog result code
        """
        dialog = HelpDialog(parent)
        
        # Navigate to topic if specified
        if topic:
            topic_path = f"{topic.lower().replace(' ', '_')}.html"
            dialog._navigate_to_page(topic_path)
        
        return dialog.exec() 