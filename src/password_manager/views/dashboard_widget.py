"""
Dashboard widget for managing password entries.
"""

from typing import List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QGroupBox, QAbstractItemView, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QAction

from password_manager.controllers.search_controller import SearchController

class DashboardWidget(QWidget):
    """Dashboard widget for managing password entries."""
    
    add_entry_requested = pyqtSignal()
    edit_entry_requested = pyqtSignal(int)
    delete_entry_requested = pyqtSignal(int)
    view_entry_requested = pyqtSignal(int)
    copy_password_requested = pyqtSignal(int)
    generate_password_requested = pyqtSignal()
    
    def __init__(self):
        """Initialize the dashboard widget."""
        super().__init__()
        self.entries = []
        self.filtered_entries = []
        self.search_controller = SearchController()
        self.setup_ui()
        self._connect_signals()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header section
        self._create_header_section(main_layout)
        
        # Search and filter section
        self._create_search_section(main_layout)
        
        # Entries table
        self._create_entries_table(main_layout)
        
        # Action buttons
        self._create_action_buttons(main_layout)
    
    def _create_header_section(self, parent_layout):
        """Create the header section with welcome message and user info."""
        header_layout = QHBoxLayout()
        
        # Welcome message
        welcome_label = QLabel("Your Vault is Ready – We're Keeping Your Logins Safe!")
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addLayout(header_layout)
    
    def _create_search_section(self, parent_layout):
        """Create the search and filter section."""
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout(search_group)
        search_layout.setSpacing(10)
        
        # Search box
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name, username, or notes...")
        self.search_edit.setMinimumHeight(30)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Filter by field
        filter_label = QLabel("Filter by:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Name", "Username", "Address", "Notes"])
        self.filter_combo.setMinimumHeight(30)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.filter_combo)
        
        # Clear search button
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.setMinimumHeight(30)
        self.clear_search_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        search_layout.addWidget(self.clear_search_button)
        
        parent_layout.addWidget(search_group)
    
    def _create_entries_table(self, parent_layout):
        """Create the entries table."""
        table_group = QGroupBox("Password Entries")
        table_layout = QVBoxLayout(table_group)
        
        # Table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(3)
        self.entries_table.setHorizontalHeaderLabels([
            "ID", "Address/Name", "Actions"
        ])
        
        # Table properties
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        self.entries_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Table style
        self.entries_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                gridline-color: #3a3a3a;
                border: 1px solid #3a3a3a;
                alternate-background-color: #252526;
            }

            QTableWidget::item {
                color: #dcdcdc;
                padding: 5px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #264f78;
                color: #ffffff;
            }

            QTableWidget::item:hover {
                background-color: #373737;
                color: #ffffff;
            }

            QHeaderView::section {
                background-color: #2a2d2e;
                color: #e0e0e0;
                padding: 6px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
            }
        """)

        
        # Column widths
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Address/Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        # Hide ID column by default
        self.entries_table.hideColumn(0)
        
        # Hide the horizontal header completely
        self.entries_table.horizontalHeader().setVisible(False)
        
        table_layout.addWidget(self.entries_table)
        
        # Entry count label
        self.entry_count_label = QLabel("No entries found")
        self.entry_count_label.setStyleSheet("color: #666; font-style: italic;")
        table_layout.addWidget(self.entry_count_label)
        
        parent_layout.addWidget(table_group)
    
    def _create_action_buttons(self, parent_layout):
        """Create the action buttons section."""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Add entry button
        self.add_entry_button = QPushButton("➕Add New Entry")
        self.add_entry_button.setMinimumHeight(40)
        self.add_entry_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
        """)
        actions_layout.addWidget(self.add_entry_button)
        
        # Generate password button
        self.generate_password_button = QPushButton("Generate Password")
        self.generate_password_button.setMinimumHeight(40)
        self.generate_password_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        # actions_layout.addWidget(self.generate_password_button)
        
        actions_layout.addStretch()
        
        parent_layout.addLayout(actions_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Button signals
        self.add_entry_button.clicked.connect(self.add_entry_requested.emit)
        self.generate_password_button.clicked.connect(self.generate_password_requested.emit)
        self.clear_search_button.clicked.connect(self._clear_search)
        
        # Search and filter signals
        self.search_edit.textChanged.connect(self._apply_search_filter)
        self.filter_combo.currentTextChanged.connect(self._apply_search_filter)
        
        # Table signals
        self.entries_table.customContextMenuRequested.connect(self._show_context_menu)
        self.entries_table.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def update_entries(self, entries: list[Dict]):
        """Update the entries table with new data."""
        self.entries = entries
        self._apply_search_filter()
    
    def _apply_search_filter(self):
        """Apply search and filter to entries using the controller."""
        search_text = self.search_edit.text()
        filter_field = self.filter_combo.currentText()
        
        # Use the search controller to filter entries
        self.filtered_entries = self.search_controller.filter_entries(
            self.entries, search_text, filter_field
        )
        
        # Update the table and count
        self._populate_table()
        self._update_entry_count()
    
    def _populate_table(self):
        """Populate the table with filtered entries."""
        self.entries_table.setRowCount(len(self.filtered_entries))
        
        for row, entry in enumerate(self.filtered_entries):
            # ID column
            id_item = QTableWidgetItem(str(entry.get('id', '')))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 0, id_item)
            
            # Name/Address column
            name = entry.get('Name', '')
            address = entry.get('Address', '')
            display_text = f"{name} - {address}" if address else name
            name_item = QTableWidgetItem(display_text)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 1, name_item)
            
            # Actions column
            actions_widget = self._create_actions_widget(entry.get('id'), entry)
            self.entries_table.setCellWidget(row, 2, actions_widget)
    
    def _create_actions_widget(self, entry_id: int, entry: Dict) -> QWidget:
        """Create the actions widget for a table row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # View button
        view_button = QPushButton("👁")
        view_button.setToolTip("View entry details")
        view_button.setFixedSize(30, 25)
        view_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        view_button.clicked.connect(lambda: self._on_view_entry_clicked(entry_id))
        layout.addWidget(view_button)
        
        # Edit button
        edit_button = QPushButton("✏")
        edit_button.setToolTip("Edit entry")
        edit_button.setFixedSize(30, 25)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #ffb900;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e6a700;
            }
        """)
        edit_button.clicked.connect(lambda: self._on_edit_entry_clicked(entry_id))
        layout.addWidget(edit_button)
        
        # Copy password button
        copy_button = QPushButton("📋")
        copy_button.setToolTip("Copy password to clipboard")
        copy_button.setFixedSize(30, 25)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
        """)
        copy_button.clicked.connect(lambda: self._on_copy_password_clicked(entry))
        layout.addWidget(copy_button)
        
        # Delete button
        delete_button = QPushButton("🗑")
        delete_button.setToolTip("Delete entry")
        delete_button.setFixedSize(30, 25)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b91d47;
            }
        """)
        delete_button.clicked.connect(lambda: self._on_delete_entry_clicked(entry_id))
        layout.addWidget(delete_button)
        
        layout.addStretch()
        return widget
    
    def _update_entry_count(self):
        """Update the entry count label using the controller."""
        count_text = self.search_controller.get_entry_count_text(self.filtered_entries)
        self.entry_count_label.setText(count_text)
    
    def _clear_search(self):
        """Clear search and filter."""
        self.search_edit.clear()
        self.filter_combo.setCurrentText("All")
        # Use the controller to clear search
        self.filtered_entries = self.search_controller.clear_search(self.entries)
        self._populate_table()
        self._update_entry_count()
    
    def _show_context_menu(self, position):
        """Show context menu for table items."""
        item = self.entries_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        entry_id_item = self.entries_table.item(row, 0)
        if not entry_id_item:
            return
        
        try:
            entry_id = int(entry_id_item.text())
        except ValueError:
            return
        
        menu = QMenu(self)
        
        # View action
        view_action = QAction("View Entry", self)
        view_action.triggered.connect(lambda: self._on_view_entry_clicked(entry_id))
        menu.addAction(view_action)
        
        # Edit action
        edit_action = QAction("Edit Entry", self)
        edit_action.triggered.connect(lambda: self._on_edit_entry_clicked(entry_id))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        # Copy password action
        copy_action = QAction("Copy Password", self)
        copy_action.triggered.connect(lambda: self._copy_password_to_clipboard(
            next((e for e in self.filtered_entries if e.get('id') == entry_id), {})
        ))
        menu.addAction(copy_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete Entry", self)
        delete_action.triggered.connect(lambda: self._on_delete_entry_clicked(entry_id))
        menu.addAction(delete_action)
        
        menu.exec(QCursor.pos())
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on table item."""
        row = item.row()
        entry_id_item = self.entries_table.item(row, 0)
        if entry_id_item:
            try:
                entry_id = int(entry_id_item.text())
                self._on_view_entry_clicked(entry_id)
            except ValueError:
                pass
    
    def _copy_password_to_clipboard(self, entry: Dict):
        """Copy password to clipboard."""
        password = entry.get('Password', '')
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self._show_status_message("Password copied to clipboard!", 2000)
        else:
            self._show_status_message("No password to copy", 2000)
    
    def _show_status_message(self, message: str, timeout: int = 0):
        """Show a status message (placeholder for future implementation)."""
        # This could be connected to a status bar or notification system
        pass
    
    def _on_copy_password_clicked(self, entry: Dict):
        """Handle copy password button click."""
        self._copy_password_to_clipboard(entry)
    
    def _on_view_entry_clicked(self, entry_id: int):
        """Handle view entry button click."""
        self.view_entry_requested.emit(entry_id)
    
    def _on_edit_entry_clicked(self, entry_id: int):
        """Handle edit entry button click."""
        self.edit_entry_requested.emit(entry_id)
    
    def _on_delete_entry_clicked(self, entry_id: int):
        """Handle delete entry button click."""
        self.delete_entry_requested.emit(entry_id) 