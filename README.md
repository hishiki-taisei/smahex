# SMASH HEX

A web application that displays Super Smash Bros. characters in a hexagonal grid layout. Perfect for character selection, team building, or just for fun!

![SMASH HEX Example](https://via.placeholder.com/800x400?text=SMASH+HEX+Example)

## Features

- **Hexagonal Grid Layout**: Characters are displayed in a visually appealing honeycomb pattern
- **Multiple Board Sizes**: Choose from 5x5, 6x6, 7x7, or 8x8 grid sizes
- **Seed-Based Generation**: Share your exact board configuration with others using seed values
- **Character Duplication**: Option to allow or disallow character duplicates on the board
- **Color Marking**: Click on characters to cycle through color states (default, red, blue)
- **URL Sharing**: Easily share your board configuration via URL

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Flask
- Character icon images in the `app/static/sma_icon/` directory

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/hishiki-taisei/smahex.git
   cd smahex
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app/app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Deployment

This application is compatible with Vercel deployment using the included `vercel.json` configuration.

## How to Use

1. **Select Board Size**: Choose from 5x5, 6x6, 7x7, or 8x8 grid sizes using the size selector
2. **Generate Boards**: 
   - Click "ランダム生成" (Random Generate) for a new random board
   - Enter a specific seed value to recreate a specific board
3. **Fighter Duplication**: Toggle "ファイター重複" checkbox to allow character duplicates
4. **Mark Characters**: Click on any character to cycle through color states:
   - Default color (no selection)
   - Red
   - Blue
5. **Share Your Board**: Click "URLをコピー" (Copy URL) to copy a shareable link

## Technical Details

- Built with Flask (Python web framework)
- Frontend uses vanilla JavaScript
- Responsive design with CSS
- Characters displayed using a mathematically correct hexagonal grid layout
- State management via URL parameters

## License

[Your License Here]

## Acknowledgments

- Character assets from Super Smash Bros.
- Hexagonal grid layout inspired by mathematical honeycomb patterns