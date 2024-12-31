# Foxhole Map Viewer

A desktop application that displays real-time map data from the Foxhole game using the official War API.

## Features
- Real-time map data visualization
- Interactive map with zoom and pan
- Accurate map backgrounds for each region
- Constant-size icons for better readability
- War report statistics display
- Auto-refresh functionality
- Map selection interface
- Dynamic updates using the Foxhole War API
- Tooltips with detailed information

## Requirements
- Python 3.8+
- PySide6
- requests
- numpy
- Pillow

## Installation
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Running the Application
Double-click the `main.py` file


## Map Images
# ONLY IF YOU WANT TO REPLACE THE EXISTING ONES
- Place map images in the `maps` directory
- Images can be in WebP, PNG, or TGA format
- Naming convention: `Map<RegionName>.(webp|png|tga)`
- Example: `MapKalokaiHex.webp`, `MapKalokaiHex.png`, or `MapKalokaiHex.tga`
- If an image is missing, a grid will be shown as fallback
- Format preference order: WebP (best compression) > PNG > TGA

## API Reference
This application uses the Foxhole War API, and my own for CPH calculations:
- Base URL: https://war-service-live.foxholeservices.com/api/
- Map Data Endpoint: /worldconquest/maps/{mapName}/dynamic/public
- War Report Endpoint: /warReport/{mapName}
- CPH War Report (Last 6 War Reports, updated every 10 minutes): https://foxholemapviewerapi-shaneeexd.pythonanywhere.com

## Map Controls
- Zoom: Use mouse wheel to zoom in/out
- Pan: Click and drag with left mouse button
- Info: Hover over icons for detailed information
- Range: Certain structures are clickable which will show range information

## Preview

![image](https://github.com/user-attachments/assets/fc57b294-4e2f-4709-9110-b86d870f0bff)

## License
MIT License
