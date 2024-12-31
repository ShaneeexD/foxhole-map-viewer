from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QCheckBox, QLabel
from PySide6.QtCore import Signal

class VisibilitySettings(QWidget):
    # Signals for when settings change
    visibility_changed = Signal(str, bool)  # (setting_name, is_visible)

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Map Visibility")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Core Structures Group
        core_group = QGroupBox("Core Structures")
        core_layout = QVBoxLayout()
        self.core_checkboxes = {
            'town_bases': QCheckBox('Town Bases'),
            'safe_houses': QCheckBox('Safe Houses'),
            'relic_bases': QCheckBox('Relic Bases'),
            'observation_towers': QCheckBox('Observation Towers'),
            'coastal_guns': QCheckBox('Coastal Guns'),
            'other': QCheckBox('Other')     
        }
        for cb in self.core_checkboxes.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.on_visibility_changed)
            core_layout.addWidget(cb)
        core_group.setLayout(core_layout)
        layout.addWidget(core_group)
        
        # Other Structures Group
        other_group = QGroupBox("Other Structures")
        other_layout = QVBoxLayout()
        self.other_checkboxes = {
            'industry': QCheckBox('Industry'),
            'storage': QCheckBox('Storage')
        }
        for cb in self.other_checkboxes.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.on_visibility_changed)
            other_layout.addWidget(cb)
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        # Resources Group
        resources_group = QGroupBox("Resources")
        resources_layout = QVBoxLayout()
        self.resource_checkboxes = {
            'components': QCheckBox('Components'),
            'sulfur': QCheckBox('Sulfur'),
            'salvage': QCheckBox('Salvage'),
            'coal-oil': QCheckBox('Coal/Oil')
        }
        for cb in self.resource_checkboxes.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.on_visibility_changed)
            resources_layout.addWidget(cb)
        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)
        
        # Text Labels Group
        text_group = QGroupBox("Location Labels")
        text_layout = QVBoxLayout()
        self.text_checkboxes = {
            'major_locations': QCheckBox('Major Locations'),
            'minor_locations': QCheckBox('Minor Locations')
        }
        for cb in self.text_checkboxes.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.on_visibility_changed)
            text_layout.addWidget(cb)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        self.setLayout(layout)
        
        # Set some basic styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 3px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        
    def on_visibility_changed(self, state):
        checkbox = self.sender()
        setting_name = None
        
        # Find which checkbox was changed
        for group in [self.core_checkboxes, self.other_checkboxes, 
                     self.resource_checkboxes, self.text_checkboxes]:
            for name, cb in group.items():
                if cb == checkbox:
                    setting_name = name
                    break
            if setting_name:
                break
        
        if setting_name:
            self.visibility_changed.emit(setting_name, bool(state))
            
    def get_visibility_state(self, setting_name):
        """Get the current state of a visibility setting"""
        for group in [self.core_checkboxes, self.other_checkboxes, 
                     self.resource_checkboxes, self.text_checkboxes]:
            if setting_name in group:
                return group[setting_name].isChecked()
        return True  # Default to visible if setting not found
