# Blueprint Viewer

![Blueprint Viewer Example](assets/blueprint_viewer_example.png)

A desktop application for visualizing Unreal Engine Blueprints. Paste blueprint text snippets and see them rendered as interactive node graphs with connections.

## Features

- **Blueprint Parsing**: Parses Unreal Engine blueprint text exports into structured node and pin data
- **Visual Rendering**: Renders nodes, pins, and wires in a clean, modern interface
- **Dynamic Sizing**: Nodes automatically resize based on the number of pins
- **Interactive Canvas**: Zoom, pan, and navigate large graphs
- **Modern UI**: Dark theme with ttk widgets and sv_ttk styling
- **Keyboard Shortcuts**: Ctrl+A (select all), Ctrl+Z/Y (undo/redo)
- **Context Menus**: Right-click for text editing options

## Installation

### Prerequisites
- Python 3.8+
- Tkinter (usually included with Python)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blueprint-viewer.git
   cd blueprint-viewer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python app/main.py
   ```

2. Paste your Unreal Engine blueprint text into the text area

3. Click "Render" to visualize the blueprint

4. Use the canvas to zoom (mouse wheel) and pan (drag)

5. Click "Clear" to reset both text and canvas

## Development

This project was developed using GitHub Copilot, leveraging AI assistance for code generation, debugging, and feature implementation.

### Project Structure
```
app/
├── blueprint/          # Blueprint parsing and data models
├── config/            # Style and configuration
├── rendering/         # Canvas rendering components
├── ui/                # UI layout components
├── views/             # Main view classes
├── widgets/           # Custom widgets
└── main.py            # Application entry point
```

### Building

To create an executable:
```bash
pyinstaller --onefile --windowed app/main.py
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and Tkinter
- Modern styling with sv_ttk
- Developed with assistance from GitHub Copilot
