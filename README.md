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

2. Add map images:
   - Create a `maps` folder in the project directory
   - Add map images in WebP or PNG format
   - Name format: `Map<RegionName>.webp` or `Map<RegionName>.png` (e.g., `MapKalokaiHex.webp` or `MapKalokaiHex.png`)

3. Run the application:
```bash
python main.py
```

## Running the Application
You can run the application in two ways:

1. Double-click the `run_viewer.bat` file
2. Or run manually with:
```bash
venv2/Scripts/python main.py
```

## Map Images
- Place map images in the `maps` directory
- Images can be in WebP, PNG, or TGA format
- Naming convention: `Map<RegionName>.(webp|png|tga)`
- Example: `MapKalokaiHex.webp`, `MapKalokaiHex.png`, or `MapKalokaiHex.tga`
- If an image is missing, a grid will be shown as fallback
- Format preference order: WebP (best compression) > PNG > TGA

## API Reference
This application uses the Foxhole War API:
- Base URL: https://war-service-live.foxholeservices.com/api/
- Map Data Endpoint: /worldconquest/maps/{mapName}/dynamic/public
- War Report Endpoint: /warReport/{mapName}

## Map Controls
- Zoom: Use mouse wheel to zoom in/out
- Pan: Click and drag with left mouse button
- Info: Hover over icons for detailed information

## License
MIT License
