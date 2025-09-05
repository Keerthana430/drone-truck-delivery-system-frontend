"""
Vehicle control panel widget - UPDATED with flexible container sizing
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QPushButton, 
                           QListWidget, QScrollArea, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

class VehicleControlPanel(QWidget):
    """Control panel for vehicle tracking"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status display with improved sizing
        status_group = QGroupBox("Vehicle Status")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ff6b35;
                font-size: 14px;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        
        # Create scrollable area for vehicle status
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                border: none;
                background: #404040;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #ff6b35;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff8c5a;
            }
        """)
        
        # UPDATED: Remove fixed height constraint and use flexible sizing
        self.status_list = QListWidget()
        self.status_list.setMinimumHeight(150)  # Minimum height instead of maximum
        # Remove the setMaximumHeight constraint to allow expansion
        
        self.status_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
                background-color: #3d3d3d;
                border: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #ff6b35;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #4d4d4d;
                border-color: #ff6b35;
            }
        """)
        
        # Set the list widget as the scroll area's widget
        scroll_area.setWidget(self.status_list)
        
        # UPDATED: Allow the status layout to expand
        status_layout.addWidget(scroll_area, 1)  # Give it stretch factor of 1
        
        # Add to main layout with expansion
        layout.addWidget(status_group, 1)  # Allow status group to expand
        
        # Optional: Add a small stretch at the bottom if needed
        # layout.addStretch(0)  # Reduced or removed stretch
    
    def update_vehicle_status(self, vehicle_data):
        """Update vehicle status in the list with improved formatting"""
        # Create detailed status text with better formatting
        status_text = f"🚁 {vehicle_data.vehicle_id}\n"
        status_text += f"Type: {vehicle_data.vehicle_type}\n"
        
        # Status with color indicators
        status_icon = "🟢" if vehicle_data.status == "Moving" else "🔴" if vehicle_data.status == "Stopped" else "🟡"
        status_text += f"Status: {status_icon} {vehicle_data.status}\n"
        
        status_text += f"Speed: {vehicle_data.speed:.1f} km/h\n"
        status_text += f"Position:\n  Lat: {vehicle_data.lat:.6f}\n  Lon: {vehicle_data.lon:.6f}"
        
        # Find existing item or create new
        found = False
        for i in range(self.status_list.count()):
            item = self.status_list.item(i)
            if vehicle_data.vehicle_id in item.text():
                item.setText(status_text)
                found = True
                break
        
        if not found:
            # Add new item with custom sizing
            item = QListWidgetItem(status_text)
            item.setSizeHint(QSize(280, 120))  # Set adequate size for multi-line text
            self.status_list.addItem(item)
        
        # UPDATED: Auto-resize to content
        self.auto_resize_list()
    
    def auto_resize_list(self):
        """Keep fixed height - no auto-resizing needed with single scrollbar approach"""
        pass  # No resizing needed as we use fixed height with scrollbar
    
    def clear_vehicle_status(self):
        """Clear all vehicle status items"""
        self.status_list.clear()
    
    def get_vehicle_count(self):
        """Get current number of vehicles being tracked"""
        return self.status_list.count()
    
    def remove_vehicle_status(self, vehicle_id):
        """Remove a specific vehicle from the status list"""
        for i in range(self.status_list.count()):
            item = self.status_list.item(i)
            if vehicle_id in item.text():
                self.status_list.takeItem(i)
                break