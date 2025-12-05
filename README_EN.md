# BIN Viewer

[中文](README.md) | English

A visualization tool for binary files, designed for operator development and model debugging to compare bin file similarity.

![Main Interface](assets/images/main.png)

## Background

During deep learning operator development, it's often necessary to compare bin file similarity of model outputs, visualize intermediate layer tensor data, and concatenate multiple tensor files. This tool was developed to improve debugging efficiency.

## Features

- **Single File View** - Visualize waveform data from bin files
- **Dual File Comparison** - Compare two files and calculate similarity (Cosine, MSE, MAE)
- **Tensor Concatenation** - Concatenate multiple bin files
- **Multi-theme/Multi-language** - Light/dark theme switching, Chinese/English interface
- **Interactive Operations** - Drag & drop files, scroll to zoom, drag to pan, right-click to save images

## Quick Start

### Requirements
- Python 3.8+

### Installation & Run

```bash
pip install PyQt5 numpy matplotlib
python main.py
```

### Build

```bash
pip install pyinstaller
pyinstaller main.spec
```

## Usage

### Basic Operations
- Drag 1 bin file → View waveform
- Drag 2 bin files → Auto comparison
- Support int8, int16, float32 data types
- Right-click to save images (SVG/PDF/PNG/JPEG)

### Shortcuts
- `ESC` - Close window
- `↑/↓` - Switch data type

### Demo

![Demo](https://raw.githubusercontent.com/WWandP/Bin-Viewer/main/assets/demo.gif)

> If GIF not displayed, please check [assets/demo.gif](assets/demo.gif)

## Project Structure

```
binviewer/
├── main.py              # Entry point
├── assets/              # Resources
│   ├── icons/          # Icons
│   ├── images/         # Images
│   └── demo.mp4        # Demo video
└── src/                 # Source code
    ├── bin_viewer.py           # Main window
    ├── plot_window.py          # Waveform window
    ├── comparison_window.py    # Comparison window
    └── tensor_concat_window.py # Concatenation tool
```

## Tech Stack

- PyQt5 - GUI framework
- NumPy - Data processing
- Matplotlib - Data visualization

## Acknowledgments

Most of the code in this project was developed with the assistance of AI tools, special thanks to Claude, Doubao, Grok and other AI tools, which greatly improved development efficiency.

Thanks also to PyQt5, NumPy, Matplotlib and other open source projects.

## License

MIT License
