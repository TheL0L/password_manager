"""
Search controller for the Password Manager.
Handles search and filtering operations for password entries.
"""

import logging
from typing import List, Dict
from PyQt6.QtCore import QObject, pyqtSignal

class SearchController(QObject):
    """Search controller for entry filtering and search operations."""
    
    search_results_updated = pyqtSignal(list)
    
    def __init__(self):
        """Initialize the search controller."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def filter_entries(self, entries: List[Dict], search_text: str, filter_field: str) -> List[Dict]:
        """Filter entries based on search text and field filter."""
        try:
            if not search_text.strip() and filter_field == "All":
                # No search criteria, return all entries
                self.search_results_updated.emit(entries)
                return entries
            
            filtered_entries = []
            search_lower = search_text.lower().strip()
            
            for entry in entries:
                if self._entry_matches_search(entry, search_lower, filter_field):
                    filtered_entries.append(entry)
            
            self.search_results_updated.emit(filtered_entries)
            self.logger.debug(f"Filtered {len(entries)} entries to {len(filtered_entries)} results")
            return filtered_entries
            
        except Exception as e:
            self.logger.error(f"Error filtering entries: {e}")
            return entries
    
    def _entry_matches_search(self, entry: Dict, search_text: str, filter_field: str) -> bool:
        """Check if an entry matches the search criteria."""
        if not search_text:
            return True
        
        if filter_field == "All":
            # Search across all relevant fields
            searchable_fields = [
                str(entry.get('Name', '')),
                str(entry.get('Address', '')),
                str(entry.get('Username', '')),
                str(entry.get('Notes', ''))
            ]
            return any(search_text in field.lower() for field in searchable_fields)
        
        elif filter_field == "Name":
            return search_text in str(entry.get('Name', '')).lower()
        elif filter_field == "Username":
            return search_text in str(entry.get('Username', '')).lower()
        elif filter_field == "Address":
            return search_text in str(entry.get('Address', '')).lower()
        elif filter_field == "Notes":
            return search_text in str(entry.get('Notes', '')).lower()
        
        return False
    
    def clear_search(self, entries: List[Dict]) -> List[Dict]:
        """Clear search and return all entries."""
        self.search_results_updated.emit(entries)
        return entries
    
    def get_entry_count_text(self, entries: List[Dict]) -> str:
        """Get formatted entry count text."""
        count = len(entries)
        if count == 0:
            return "No entries found"
        elif count == 1:
            return "1 entry found"
        else:
            return f"{count} entries found" 