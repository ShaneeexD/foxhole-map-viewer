import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QComboBox, QPushButton, QLabel, QScrollArea, QSplitter, QToolTip, QTextEdit, QGroupBox, QHBoxLayout, QListWidget)
from PySide6.QtCore import QTimer, Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QWheelEvent, QMouseEvent, QImage
from api_client import FoxholeAPI
from map_icons import IconType, TeamID, ICON_COLORS, ICON_SYMBOLS, STRUCTURE_RANGES, ICON_PATHS, TEAM_COLORED_STRUCTURES, ORANGE_COLORED_STRUCTURES, YELLOW_COLORED_STRUCTURES, GREY_COLORED_STRUCTURES, BRIGHT_ORANGE_COLORED_STRUCTURES, STRUCTURE_COLORS
import numpy as np
import os
import traceback

class MapView(QWidget):
    def __init__(self, visibility_settings=None, parent=None):
        super().__init__(parent)
        self.api = FoxholeAPI()  # Initialize the API client
        self.visibility_settings = visibility_settings
        self.map_data = None
        self.static_map_data = None  # Store static map data
        self.map_image = None
        self.current_map = None
        self.selected_structure = None  # Store selected structure for range display
        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_pos = None
        self.min_scale = 0.8  # Increased minimum zoom
        self.max_scale = 4.0  # Keep max zoom
        self.zoom_factor = 1.1  # Smoother zoom steps
        self.setMinimumSize(800, 800)
        self.setStyleSheet("background-color: #2b2b2b;")
        self.setMouseTracking(True)

        # Initialize view transformation

    def set_map_data(self, data, map_name):
        self.map_data = data
        if self.current_map != map_name:
            self.current_map = map_name
            self.load_map_image(map_name)
            # Always fetch static data when map changes, ETags will handle caching
            self.static_map_data = self.api.get_static_map_data(map_name)
        self.update()

    def load_map_image(self, map_name):
        """Load the map background image from WebP, PNG, or TGA"""
        # Try each format in order of preference
        for ext in ['.webp', '.png', '.tga']:
            map_path = os.path.join("maps", f"Map{map_name}{ext}")
            if os.path.exists(map_path):
                self.map_image = QImage(map_path)
                if not self.map_image.isNull():
                    # Set high-quality image scaling with 3x resolution
                    self.map_image = self.map_image.scaled(
                        self.map_image.width() * 3,  # Triple the resolution
                        self.map_image.height() * 3,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    return
        
        print(f"Warning: Map image not found for {map_name} (tried .webp, .png, and .tga)")
        self.map_image = None

    def wheelEvent(self, event: QWheelEvent):
        # Get the position before zoom
        old_pos = self.screen_to_scene(event.position())
        
        # Calculate new scale
        if event.angleDelta().y() > 0:
            self.scale = min(self.scale * self.zoom_factor, self.max_scale)
        else:
            self.scale = max(self.scale / self.zoom_factor, self.min_scale)
            
        # Get the position after zoom
        new_pos = self.screen_to_scene(event.position())
        
        # Adjust pan to keep the point under cursor
        self.pan_x += (new_pos.x() - old_pos.x()) * self.scale
        self.pan_y += (new_pos.y() - old_pos.y()) * self.scale
        
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Store position for panning
            self.last_mouse_pos = event.position()
            
            # Check if we clicked on a structure with range
            if self.map_data and 'mapItems' in self.map_data:
                base_rect = self.get_base_rect()
                
                for item in self.map_data['mapItems']:
                    # Skip if item is not visible according to settings
                    if not self.should_draw_item(item):
                        continue
                        
                    if item['iconType'] in STRUCTURE_RANGES:
                        # Calculate item position
                        x = base_rect.left() + item['x'] * base_rect.width()
                        y = base_rect.top() + item['y'] * base_rect.height()
                        screen_x = x * self.scale + self.pan_x
                        screen_y = y * self.scale + self.pan_y
                        
                        # Check if click is within icon bounds
                        dx = event.position().x() - screen_x
                        dy = event.position().y() - screen_y
                        if (dx * dx + dy * dy) < 225:  # 15*15 radius
                            # Toggle selection
                            if self.selected_structure == item:
                                self.selected_structure = None
                            else:
                                self.selected_structure = item
                            self.update()
                            return

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def mouseMoveEvent(self, event: QMouseEvent):
        # Handle panning
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.position()
            self.update()
        
        # Handle tooltips
        if self.map_data and 'mapItems' in self.map_data:
            pos = event.position()
            base_rect = self.get_base_rect()
            
            # Check if mouse is over any item
            for item in self.map_data['mapItems']:
                # Skip if item is not visible according to settings
                if not self.should_draw_item(item):
                    continue
                    
                # Calculate scaled position
                x = base_rect.left() + item['x'] * base_rect.width()
                y = base_rect.top() + item['y'] * base_rect.height()
                
                # Apply pan and zoom to position
                screen_x = x * self.scale + self.pan_x
                screen_y = y * self.scale + self.pan_y
                
                # Calculate distance to item center
                dx = pos.x() - screen_x
                dy = pos.y() - screen_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # If mouse is within item radius (constant size)
                if distance < 15:
                    tooltip = self.create_tooltip(item)
                    QToolTip.showText(event.globalPosition().toPoint(), tooltip)
                    return
            
            QToolTip.hideText()

    def create_tooltip(self, item):
        """Create a tooltip for a map item"""
        icon_type = item['iconType']
        team = item['teamId']
        flags = item['flags']
        
        # Get the structure name from the icon type
        structure_name = "Unknown Structure"
        for icon_enum in IconType:
            if icon_enum.value == icon_type:
                structure_name = icon_enum.name.replace('_', ' ').title()
                break
        
        # Get team name and color
        team_name = "Neutral"
        team_color = "#9B9B9B"
        if team == TeamID.WARDENS.value:
            team_name = "Wardens"
            team_color = "#4A90E2"
        elif team == TeamID.COLONIALS.value:
            team_name = "Colonials"
            team_color = "#7ED321"

        # Format the flags into a readable list
        flag_list = []
        if flags & 0x01:  # Built
            flag_list.append("Built")
        if flags & 0x02:  # Damaged
            flag_list.append("Damaged")
        if flags & 0x04:  # Destroyed
            flag_list.append("Destroyed")
        
        # Create a styled tooltip using HTML with minimal styling
        tooltip = f"""
        <div style='background-color: white; padding: 4px 8px; border-radius: 4px;'>
            <b style='color: #333;'>{structure_name}</b><br>
            <span style='color: {team_color};'>{team_name}</span><br>
            <span style='color: #666; font-size: 90%;'>{item['x']:.1f}, {item['y']:.1f}</span>
        </div>
        """
        return tooltip.strip()

    def screen_to_scene(self, screen_pos):
        """Convert screen coordinates to scene coordinates"""
        x = (screen_pos.x() - self.pan_x) / self.scale
        y = (screen_pos.y() - self.pan_y) / self.scale
        return QPointF(x, y)

    def scene_to_screen(self, scene_pos):
        """Convert scene coordinates to screen coordinates"""
        x = scene_pos.x() * self.scale + self.pan_x
        y = scene_pos.y() * self.scale + self.pan_y
        return QPointF(x, y)

    def get_base_rect(self):
        """Calculate the aspect-ratio corrected base rectangle"""
        view_size = min(self.width(), self.height())
        margin = 50
        base_rect = QRectF(margin, margin, view_size - 2*margin, view_size - 2*margin)
        
        if self.map_image:
            img_aspect = self.map_image.width() / self.map_image.height()
            scaled_rect = QRectF(base_rect)
            
            if img_aspect > 1:  # Image is wider than tall
                new_height = scaled_rect.width() / img_aspect
                height_diff = scaled_rect.height() - new_height
                scaled_rect.adjust(0, height_diff/2, 0, -height_diff/2)
            elif img_aspect < 1:  # Image is taller than wide
                new_width = scaled_rect.height() * img_aspect
                width_diff = scaled_rect.width() - new_width
                scaled_rect.adjust(width_diff/2, 0, -width_diff/2, 0)
            
            return scaled_rect
        
        return base_rect

    def paintEvent(self, event):
        if not self.map_data:
            return

        painter = QPainter(self)
        try:
            # Enable available high-quality rendering hints
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing |
                QPainter.RenderHint.SmoothPixmapTransform |
                QPainter.RenderHint.TextAntialiasing
            )
            
            base_rect = self.get_base_rect()

            painter.save()
            try:
                painter.translate(self.pan_x, self.pan_y)
                painter.scale(self.scale, self.scale)
                
                if self.map_image:
                    painter.drawImage(base_rect, self.map_image)
                else:
                    self._draw_grid(painter, base_rect)

                # Draw range circle for selected structure
                if self.selected_structure:
                    x = base_rect.left() + self.selected_structure['x'] * base_rect.width()
                    y = base_rect.top() + self.selected_structure['y'] * base_rect.height()
                    
                    # Get range and team color
                    structure_range = STRUCTURE_RANGES[self.selected_structure['iconType']]
                    team_id = TeamID(self.selected_structure['teamId'])
                    team_color = QColor(ICON_COLORS.get(team_id, "#808080"))
                    
                    if isinstance(structure_range, dict):  # Coastal gun with inner/outer ranges
                        # Draw outer circle (dark orange)
                        outer_radius = structure_range['outer'] * base_rect.width()
                        painter.setPen(QPen(QColor(255, 140, 0, 100), 2))
                        painter.setBrush(QBrush(QColor(255, 140, 0, 30)))
                        painter.drawEllipse(QPointF(x, y), outer_radius, outer_radius)
                        
                        # Draw inner circle (red)
                        inner_radius = structure_range['inner'] * base_rect.width()
                        painter.setPen(QPen(QColor(255, 0, 0, 100), 2))
                        painter.setBrush(QBrush(QColor(255, 0, 0, 30)))
                        painter.drawEllipse(QPointF(x, y), inner_radius, inner_radius)
                    else:  # Single range circle with team color
                        radius = structure_range * base_rect.width()
                        # Set slightly transparent team color
                        range_color = QColor(team_color)
                        range_color.setAlpha(100)  # Border
                        fill_color = QColor(team_color)
                        fill_color.setAlpha(75)   # Fill
                        
                        painter.setPen(QPen(range_color, 2))
                        painter.setBrush(QBrush(fill_color))
                        painter.drawEllipse(QPointF(x, y), radius, radius)
            finally:
                painter.restore()

            # Draw items at constant size
            painter.save()
            try:
                if 'mapItems' in self.map_data:
                    for item in self.map_data['mapItems']:
                        # Check visibility settings based on icon type
                        if not self.should_draw_item(item):
                            continue

                        # Calculate scaled position using the aspect-ratio corrected base_rect
                        x = base_rect.left() + item['x'] * base_rect.width()
                        y = base_rect.top() + item['y'] * base_rect.height()
                        
                        # Apply pan and zoom to position only
                        screen_x = x * self.scale + self.pan_x
                        screen_y = y * self.scale + self.pan_y
                        
                        self._draw_map_item(painter, item, screen_x, screen_y)
            finally:
                painter.restore()

            # Draw text labels last so they appear on top
            painter.save()
            try:
                painter.translate(self.pan_x, self.pan_y)
                painter.scale(self.scale, self.scale)

                if self.static_map_data and 'mapTextItems' in self.static_map_data:
                    # Save current transform and reset scale for text
                    painter.save()
                    painter.scale(1/self.scale, 1/self.scale)  # Counter the scale for text
                    
                    font = painter.font()
                    # Major locations get larger font
                    major_font = QFont(font)
                    major_font.setPointSize(12)
                    major_font.setBold(True)
                    
                    # Minor locations get smaller font
                    minor_font = QFont(font)
                    minor_font.setPointSize(10)
                    
                    for text_item in self.static_map_data['mapTextItems']:
                        # Check visibility settings for text
                        if not self.should_draw_text(text_item):
                            continue

                        # Calculate position in scaled coordinates
                        map_x = base_rect.left() + text_item['x'] * base_rect.width()
                        map_y = base_rect.top() + text_item['y'] * base_rect.height()
                        
                        # Convert to screen coordinates
                        screen_x = map_x * self.scale
                        screen_y = map_y * self.scale
                        
                        # Set font based on marker type
                        if text_item['mapMarkerType'] == 'Major':
                            painter.setFont(major_font)
                        else:
                            painter.setFont(minor_font)
                        
                        # Draw text with shadow for better visibility
                        text_rect = painter.fontMetrics().boundingRect(text_item['text'])
                        text_x = screen_x - text_rect.width() / 2
                        text_y = screen_y + text_rect.height() / 2
                        
                        # Draw shadow
                        painter.setPen(Qt.black)
                        painter.drawText(text_x + 1, text_y + 1, text_item['text'])
                        
                        # Draw text
                        painter.setPen(Qt.white)
                        painter.drawText(text_x, text_y, text_item['text'])
                    
                    # Restore transform for other elements
                    painter.restore()
            finally:
                painter.restore()
        finally:
            painter.end()

    def should_draw_item(self, item):
        """Check if an item should be drawn based on visibility settings"""
        if not self.visibility_settings:
            return True
            
        icon_type = item['iconType']
        
        # Core structures
        if icon_type in [IconType.TOWN_BASE_1.value, IconType.TOWN_BASE_2.value, IconType.TOWN_BASE_3.value]:
            return self.visibility_settings.get_visibility_state('town_bases')
        elif icon_type == IconType.GARRISON_STATION.value:
            return self.visibility_settings.get_visibility_state('safe_houses')
        elif icon_type in [IconType.RELIC_BASE_1.value, IconType.RELIC_BASE_2.value, IconType.RELIC_BASE_3.value]:
            return self.visibility_settings.get_visibility_state('relic_bases')
        elif icon_type == IconType.OBSERVATION_TOWER.value:
            return self.visibility_settings.get_visibility_state('observation_towers')
        elif icon_type == IconType.COASTAL_GUN.value:
            return self.visibility_settings.get_visibility_state('coastal_guns')
        elif icon_type == IconType.HOSPITAL.value:
            return self.visibility_settings.get_visibility_state('other')
        
        # Industry
        elif icon_type in [IconType.FACTORY.value, IconType.MASS_PRODUCTION_FACTORY.value, 
                         IconType.REFINERY.value, IconType.CONSTRUCTION_YARD.value,
                         IconType.VEHICLE_FACTORY.value, IconType.TECH_CENTER.value, IconType.MORTAR_HOUSE.value]:
            return self.visibility_settings.get_visibility_state('industry')
        elif icon_type in [IconType.SEAPORT.value, IconType.SHIPYARD.value, IconType.STORAGE_FACILITY.value,]:
            return self.visibility_settings.get_visibility_state('storage')
        
        # Resources
        elif icon_type in [IconType.COMPONENT_MINE.value, IconType.COMPONENT_FIELD.value]:
            return self.visibility_settings.get_visibility_state('components')
        elif icon_type in [IconType.SULFUR_MINE.value, IconType.SULFUR_FIELD.value]:
            return self.visibility_settings.get_visibility_state('sulfur')
        elif icon_type in [IconType.SALVAGE_MINE.value, IconType.SALVAGE_FIELD.value]:
            return self.visibility_settings.get_visibility_state('salvage')
        elif icon_type in [IconType.COAL_FIELD.value, IconType.OIL_FIELD.value, IconType.FACILITY_MINE_OIL_RIG.value]:
            return self.visibility_settings.get_visibility_state('coal-oil')
        
        return True  # Show by default if not categorized

    def should_draw_text(self, text_item):
        """Check if a text item should be drawn based on visibility settings"""
        if not self.visibility_settings:
            return True
            
        if text_item['mapMarkerType'] == 'Major':
            return self.visibility_settings.get_visibility_state('major_locations')
        else:
            return self.visibility_settings.get_visibility_state('minor_locations')

    def _draw_grid(self, painter, rect):
        # Draw grid lines
        pen = QPen(QColor("#3a3a3a"))
        painter.setPen(pen)
        
        grid_size = 10
        step_x = rect.width() / grid_size
        step_y = rect.height() / grid_size

        for i in range(grid_size + 1):
            x = rect.left() + i * step_x
            y = rect.top() + i * step_y
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

    def _draw_map_item(self, painter: QPainter, item, x, y):
        """Draw a map item at the specified screen coordinates."""
        try:
            icon_type = IconType(item.get('iconType', -1))
            team_id = TeamID(item.get('teamId', 'NONE'))
            
            # Get icon path
            icon_path = ICON_PATHS.get(icon_type)
            if icon_path:
                # Try to load TGA first
                image = QImage(icon_path)
                if image.isNull():
                    # If TGA fails, try PNG
                    png_path = icon_path.replace('.TGA', '.png').replace('.tga', '.png')
                    image = QImage(png_path)
                    if image.isNull():
                        print(f"Failed to load both TGA and PNG for: {icon_path}")
                        return self._draw_emoji_fallback(painter, icon_type, x, y)
                    else:
                        # Convert PNG to ARGB32 format if it's in indexed format
                        if image.format() == QImage.Format.Format_Indexed8:
                            image = image.convertToFormat(QImage.Format.Format_ARGB32)
            
                # Calculate icon size (32x32 pixels)
                icon_size = 32
                
                # Center the icon at the target position
                icon_rect = QRectF(x - icon_size/2, y - icon_size/2, icon_size, icon_size)
                
                # Apply team colors to appropriate structures
                if icon_type in TEAM_COLORED_STRUCTURES and team_id != TeamID.NONE:
                    # First draw the original image
                    painter.drawImage(icon_rect, image)
                    
                    # Create darker color overlay
                    colored_image = image.copy()
                    img_painter = QPainter(colored_image)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    team_color = QColor(ICON_COLORS.get(team_id, "#808080"))
                    team_color.setAlpha(180)  # 70% opacity
                    img_painter.fillRect(colored_image.rect(), team_color)
                    img_painter.end()
                    
                    # Draw the colored overlay with multiply blend mode
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                    painter.drawImage(icon_rect, colored_image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                elif icon_type in ORANGE_COLORED_STRUCTURES:
                    painter.drawImage(icon_rect, image)
                    colored_image = image.copy()
                    img_painter = QPainter(colored_image)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    color = QColor(STRUCTURE_COLORS["ORANGE"])
                    color.setAlpha(180)
                    img_painter.fillRect(colored_image.rect(), color)
                    img_painter.end()
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                    painter.drawImage(icon_rect, colored_image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                elif icon_type in BRIGHT_ORANGE_COLORED_STRUCTURES:
                    painter.drawImage(icon_rect, image)
                    colored_image = image.copy()
                    img_painter = QPainter(colored_image)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    color = QColor(STRUCTURE_COLORS["BRIGHT_ORANGE"])
                    color.setAlpha(180)
                    img_painter.fillRect(colored_image.rect(), color)
                    img_painter.end()
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                    painter.drawImage(icon_rect, colored_image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                elif icon_type in YELLOW_COLORED_STRUCTURES:
                    painter.drawImage(icon_rect, image)
                    colored_image = image.copy()
                    img_painter = QPainter(colored_image)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    color = QColor(STRUCTURE_COLORS["YELLOW"])
                    color.setAlpha(180)
                    img_painter.fillRect(colored_image.rect(), color)
                    img_painter.end()
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                    painter.drawImage(icon_rect, colored_image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                elif icon_type in GREY_COLORED_STRUCTURES:
                    painter.drawImage(icon_rect, image)
                    colored_image = image.copy()
                    img_painter = QPainter(colored_image)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    color = QColor(STRUCTURE_COLORS["DARK_GREY"])
                    color.setAlpha(180)
                    img_painter.fillRect(colored_image.rect(), color)
                    img_painter.end()
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
                    painter.drawImage(icon_rect, colored_image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                else:
                    # Draw the original image for other icons
                    painter.drawImage(icon_rect, image)
            else:
                print(f"Icon path not found: {icon_path} for {icon_type.name} - Team: {team_id.name}")  # Debug logging
                self._draw_emoji_fallback(painter, icon_type, x, y)
                
        except (ValueError, KeyError) as e:
            print(f"Error drawing map item: {e}")
            self._draw_emoji_fallback(painter, None, x, y)

    def _draw_emoji_fallback(self, painter, icon_type, x, y):
        symbol = ICON_SYMBOLS.get(icon_type, "❓")
        color = ICON_COLORS.get(TeamID.NONE, "#808080")
        
        painter.setPen(QPen(QColor(color)))
        painter.setFont(QFont("Segoe UI Emoji", 12))
        painter.drawText(QRectF(x - 10, y - 10, 20, 20), Qt.AlignCenter, symbol)

    def on_visibility_changed(self, setting_name, is_visible):
        """Handle visibility changes from the settings panel"""
        # If we have a selected structure and its visibility is turned off, clear the selection
        if self.selected_structure and not is_visible:
            # Check if this visibility change affects our selected structure
            if not self.should_draw_item(self.selected_structure):
                self.selected_structure = None
                self.update()
                
        # Redraw the map with updated visibility
        self.update()

class MapViewer(QMainWindow):
    # List of available maps in Foxhole
    AVAILABLE_MAPS = [
        "Acrithia",
        "AllodsBight",
        "AshFields",
        "BasinSionnach",
        "CallahansPassage",
        "CallumsCape",
        "Clahstra",
        "ClansheadValley",
        "DeadLands",
        "DrownedVale",
        "EndlessShore",
        "FarranacCoast",
        "FishermansRow",
        "Godcrofts",
        "GreatMarch",
        "Heartlands",
        "HowlCounty",
        "Kalokai",
        "KingsCage",
        "LinnMercy",
        "LochMor",
        "MarbanHollow",
        "MooringCounty",
        "MorgensCrossing",
        "NevishLine",
        "Oarbreaker",
        "Origin",
        "ReachingTrail",
        "ReaversPass",
        "RedRiver",
        "Sableport",
        "ShackledChasm",
        "SpeakingWoods",
        "StemaLanding",
        "StlicanShelf",
        "Stonecradle",
        "TempestIsland",
        "Terminus",
        "TheFingers",
        "UmbralWildwood",
        "ViperPit",
        "WeatheredExpanse",
        "Westgate"
    ]

    def __init__(self):
        super().__init__()
        self.api = FoxholeAPI()
        self.current_map = None
        self.map_data = None
        self.war_report = None
        self.map_casualties = {}  # Store casualties for each map
        self.war_reports_file = "war_reports.json"
        
        # Load previous war reports
        try:
            with open(self.war_reports_file, 'r') as f:
                data = json.load(f)
                self.previous_war_reports = data.get('reports', [])  # List of historical reports
        except (FileNotFoundError, json.JSONDecodeError):
            self.previous_war_reports = []
        
        # Create visibility settings first
        from settings_panel import VisibilitySettings
        self.visibility_settings = VisibilitySettings()
        self.visibility_settings.visibility_changed.connect(self.on_visibility_changed)
        
        # Initialize UI before fetching any data
        self.init_ui()
        
        # Initial war reports update for red dots
        self.update_war_reports()
        
        # Set up update timer for map data
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_map_data)
        self.update_timer.start(30000)  # Update every 30 seconds
        
        # Set up timer for war reports
        self.war_reports_timer = QTimer()
        self.war_reports_timer.timeout.connect(self.update_war_reports)
        self.war_reports_timer.start(600000)  # Update every 10 minutes

    def get_api_map_name(self, map_name):
        """Convert map name to API format"""
        # Strip any activity indicators
        for indicator in ["🔴", "🟠", "🟡"]:
            if indicator in map_name:
                map_name = map_name.replace(indicator, "").strip()
        
        # Remove spaces
        map_name = map_name.replace(' ', '')
        
        # Special case for MarbanHollow
        if map_name == "MarbanHollow":
            return map_name
        
        # Add Hex suffix for other maps
        return f"{map_name}Hex"

    def get_casualties_per_hour(self, map_name):
        """Calculate casualties per hour using last 6 entries from war_reports.json"""
        if not self.previous_war_reports or len(self.previous_war_reports) < 2:
            print(f"Not enough reports to calculate CPH (have {len(self.previous_war_reports)})")
            return (0, 0)
            
        # Get last 6 reports (1 hour of data at 10 minute intervals)
        recent_reports = self.previous_war_reports[-6:]
        print(f"Using {len(recent_reports)} recent reports for CPH calculation")
        
        # Extract base map name without "Hex" suffix
        base_map_name = map_name.replace("Hex", "")
        
        # Get casualties from first and last report
        first_report = recent_reports[0].get(base_map_name, {})
        last_report = recent_reports[-1].get(base_map_name, {})
        
        if not first_report or not last_report:
            print(f"No reports found for map {map_name}")
            print(f"First report keys: {first_report.keys() if first_report else 'None'}")
            print(f"Last report keys: {last_report.keys() if last_report else 'None'}")
            return (0, 0)
            
        # Calculate casualties for each faction
        first_colonial = first_report.get('colonialCasualties', 0)
        first_warden = first_report.get('wardenCasualties', 0)
        last_colonial = last_report.get('colonialCasualties', 0)
        last_warden = last_report.get('wardenCasualties', 0)
        
        print(f"First report: Colonial={first_colonial}, Warden={first_warden}")
        print(f"Last report: Colonial={last_colonial}, Warden={last_warden}")
        
        colonial_casualties = max(0, last_colonial - first_colonial)
        warden_casualties = max(0, last_warden - first_warden)
        
        print(f"Colonial casualties over 1 hour: {colonial_casualties}")
        print(f"Warden casualties over 1 hour: {warden_casualties}")
        
        # Calculate CPH (6 reports = 1 hour)
        return (colonial_casualties, warden_casualties)

    def get_activity_indicator(self, casualties_per_hour):
        """Return appropriate activity indicator based on casualties per hour"""
        # Sum both factions' casualties for activity calculation
        total_cph = sum(casualties_per_hour)
        if total_cph >= 1001:
            return "🔴"  # Red dot for very high activity
        elif total_cph >= 501:
            return "🟠"  # Orange dot for high activity
        elif total_cph >= 50:
            return "🟡"  # Yellow dot for moderate activity
        return ""  # No dot for low activity

    def count_structures(self, map_name):
        """Count structures for each faction in a map"""
        map_data = self.api.get_map_data(self.get_api_map_name(map_name))
        if not map_data or 'mapItems' not in map_data:
            return {'WARDENS': 0, 'COLONIALS': 0}
            
        counts = {'WARDENS': 0, 'COLONIALS': 0}
        for item in map_data['mapItems']:
            if item['teamId'] == 'WARDENS':
                counts['WARDENS'] += 1
            elif item['teamId'] == 'COLONIALS':
                counts['COLONIALS'] += 1
        return counts

    def update_war_reports(self):
        """Fetch war reports for all maps and update the combo box with indicators and faction control colors"""
        current_reports = {}
        
        # Fetch current war reports for all maps
        for map_name in self.AVAILABLE_MAPS:
            try:
                report = self.api.get_war_report(self.get_api_map_name(map_name))
                if report:
                    current_reports[map_name] = report
            except Exception as e:
                print(f"Error fetching war report for {map_name}: {e}")
        
        # Add current reports to history and maintain 2-hour window (12 reports)
        self.previous_war_reports.append(current_reports)
        if len(self.previous_war_reports) > 12:
            self.previous_war_reports.pop(0)
        
        # Save reports history
        try:
            with open(self.war_reports_file, 'w') as f:
                json.dump({'reports': self.previous_war_reports}, f)
        except Exception as e:
            print(f"Error saving war reports: {e}")
        
        # Get current selection without any indicators
        current_text = self.map_combo.currentText()
        for indicator in ["🔴", "🟠", "🟡"]:
            if indicator in current_text:
                current_text = current_text.replace(indicator, "").strip()
                break
            
        # Update combo box items with activity indicators and faction control colors
        self.map_combo.clear()
        self.map_combo.addItem("Select a map...")
        
        # Add maps with appropriate activity indicators and colors
        for map_name in sorted(self.AVAILABLE_MAPS):
            # Get activity indicator
            casualties_per_hour = self.get_casualties_per_hour(map_name)
            indicator = self.get_activity_indicator(casualties_per_hour)
            
            # Count structures and determine faction control
            structure_counts = self.count_structures(map_name)
            if structure_counts['WARDENS'] > structure_counts['COLONIALS']:
                color = "blue"
            elif structure_counts['COLONIALS'] > structure_counts['WARDENS']:
                color = "green"
            else:
                color = "black"
            
            # Create styled text with color and indicator
            display_text = f"{map_name} {indicator}" if indicator else map_name
            self.map_combo.addItem(display_text)
            self.map_combo.setItemData(self.map_combo.count() - 1, QColor(color), Qt.ForegroundRole)
                
        # Restore the previous selection
        for i in range(self.map_combo.count()):
            item_text = self.map_combo.itemText(i)
            if current_text in item_text:  # This will match the map name regardless of indicator
                self.map_combo.setCurrentIndex(i)
                break

    def init_ui(self):
        self.setWindowTitle('Foxhole Map Viewer')
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel for controls and info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Map selection
        self.map_combo = QComboBox()
        self.map_combo.currentTextChanged.connect(self.on_map_selected)
        left_layout.addWidget(QLabel("Select Map:"))
        
        # Add "Select a map..." as first item
        self.map_combo.addItem("Select a map...")
        
        # Get map names and sort them alphabetically
        map_names = sorted([name for name in self.AVAILABLE_MAPS])
        self.map_combo.addItems(map_names)
        
        # Set default selection to "Select a map..."
        self.map_combo.setCurrentIndex(0)
        self.current_map = None
        
        left_layout.addWidget(self.map_combo)

        # War Report Section
        war_report_group = QWidget()
        war_report_layout = QVBoxLayout(war_report_group)
        war_report_layout.addWidget(QLabel("War Report"))
        
        self.total_enlistments_label = QLabel("Total Enlistments: -")
        self.colonial_casualties_label = QLabel("Colonial Casualties: -")
        self.warden_casualties_label = QLabel("Warden Casualties: -")
        self.colonial_cph_label = QLabel("Colonial CPH: -")
        self.warden_cph_label = QLabel("Warden CPH: -")
        self.day_of_war_label = QLabel("Day of War: -")
        
        war_report_layout.addWidget(self.total_enlistments_label)
        war_report_layout.addWidget(self.colonial_casualties_label)
        war_report_layout.addWidget(self.warden_casualties_label)
        war_report_layout.addWidget(self.colonial_cph_label)
        war_report_layout.addWidget(self.warden_cph_label)
        war_report_layout.addWidget(self.day_of_war_label)
        
        left_layout.addWidget(war_report_group)

        # Legend
        legend_group = QGroupBox("Map Activity Legend")
        legend_layout = QVBoxLayout()
        
        # Add legend items
        legend_items = [
            ("🔴", "High Activity"),
            ("🟠", "Medium Activity"),
            ("🟡", "Low Activity")
        ]
        
        for icon, description in legend_items:
            item_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            desc_label = QLabel(description)
            item_layout.addWidget(icon_label)
            item_layout.addWidget(desc_label)
            item_layout.addStretch()
            legend_layout.addLayout(item_layout)
        
        legend_group.setLayout(legend_layout)
        legend_group.setMaximumHeight(120)
        left_layout.addWidget(legend_group)

        # Info display
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        left_layout.addWidget(QLabel("Map Information:"))
        left_layout.addWidget(self.info_display)

        # Add left panel to splitter
        left_panel_scroll = QScrollArea()
        left_panel_scroll.setWidget(left_panel)
        left_panel_scroll.setWidgetResizable(True)
        splitter.addWidget(left_panel_scroll)

        # Map view with visibility settings
        self.map_view = MapView(visibility_settings=self.visibility_settings)
        splitter.addWidget(self.map_view)

        # Add settings panel
        settings_scroll = QScrollArea()
        settings_scroll.setWidget(self.visibility_settings)
        settings_scroll.setWidgetResizable(True)
        splitter.addWidget(settings_scroll)

        # Set splitter sizes (left panel : map : settings)
        splitter.setSizes([250, 700, 250])

    def on_map_selected(self, map_name):
        """Handle map selection"""
        if map_name == "Select a map...":
            self.current_map = None
        else:
            # Remove red dot if present
            if map_name.startswith("🔴 "):
                map_name = map_name[2:].strip()
            self.current_map = self.get_api_map_name(map_name)
        self.update_map_data()

    def update_war_report(self):
        """Update the war report display with the latest data"""
        if not self.current_map:
            return
            
        try:
            self.war_report = self.api.get_war_report(self.current_map)
            
            self.total_enlistments_label.setText(f"Total Enlistments: {self.war_report.get('totalEnlistments', '-')}")
            self.colonial_casualties_label.setText(f"Colonial Casualties: {self.war_report.get('colonialCasualties', '-')}")
            self.warden_casualties_label.setText(f"Warden Casualties: {self.war_report.get('wardenCasualties', '-')}")
            
            # Calculate and display CPH values with colored labels
            colonial_cph, warden_cph = self.get_casualties_per_hour(self.current_map)
            
            # Determine colors for CPH values
            colonial_color = "red" if colonial_cph > warden_cph else "green"
            warden_color = "red" if warden_cph > colonial_cph else "green"
            
            # Set styled text for Colonial CPH (green label, colored number)
            self.colonial_cph_label.setText(
                f"<span style='color: #7ED321;'>Colonial CPH: </span>"
                f"<span style='color: {colonial_color};'>{int(colonial_cph)}</span>"
            )
            
            # Set styled text for Warden CPH (blue label, colored number)
            self.warden_cph_label.setText(
                f"<span style='color: #4A90E2;'>Warden CPH: </span>"
                f"<span style='color: {warden_color};'>{int(warden_cph)}</span>"
            )
            
            day_of_war = self.war_report.get('dayOfWar')
            if day_of_war is not None:
                self.day_of_war_label.setText(f"Day of War: {day_of_war}")
            else:
                print(f"Warning: No dayOfWar value found in war report for {self.current_map}")
                self.day_of_war_label.setText("Day of War: -")
        except Exception as e:
            print(f"Error updating war report: {e}")

    def update_map_data(self):
        """Update both map data and war report"""
        if not self.current_map:
            return
            
        try:
            self.map_data = self.api.get_map_data(self.current_map)
            # Always fetch static data, ETags will handle caching
            self.map_view.static_map_data = self.api.get_static_map_data(self.current_map)
            self.map_view.set_map_data(self.map_data, self.current_map)
            self.update_war_report()
            self.format_map_data()
        except Exception as e:
            print(f"Error updating map data: {e}")
            traceback.print_exc()

    def format_map_data(self):
        info_text = [
            f"Region ID: {self.map_data.get('regionId', 'N/A')}",
            f"Last Updated: {self.map_data.get('lastUpdated', 'N/A')}",
            f"Version: {self.map_data.get('version', 'N/A')}",
            f"Total Items: {len(self.map_data.get('mapItems', []))}"
        ]
        self.info_display.setText("\n".join(info_text))

    def on_visibility_changed(self, setting_name, is_visible):
        """Handle visibility changes from the settings panel"""
        if hasattr(self, 'map_view'):
            self.map_view.on_visibility_changed(setting_name, is_visible)
            self.map_view.update()  # Trigger a redraw of the map

def main():
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
