# Drone Data Parser

Python scripts for processing and analyzing DJI drone survey data

## Author

**Eric Tannant**

- Originally created: 2021
- Last Updated: August 2025
- Version: 1.6
- License: MIT

## Overview

This project contains specialized modules for drone data processing:

1. **Camera Position Calculator** - Correlates drone images with GPS coordinates
2. **DXF Vertex Reader** - Advanced 3D vertex extraction with geological analysis and variance calculations
3. **RINEX OBS File Corrector** - Fixes formatting issues in GPS observation files
4. **Legacy Scripts** - Previous versions now largely obsolette (DXF point reader, Pix4D analysis)

## Modules

### 1. Camera Position Calculator (`camera_pos_calculator.py`)

Calculates accurate camera positions for drone images by correlating timestamp data with RINEX GPS positioning data.

**Features:**

- Processes jpg files
- Interpolates GPS positions based on image timestamps
- Applies offset corrections for precise positioning

**Requirements:**

- JPG/jpg image files (format: `prefix_prefix_ID.jpg`)
- `.pos` RINEX positioning file
- `.MRK` timestamp file
- Python packages: `pandas`

**Output:**

- `Camera_coords.csv` - CSV file with image names and corrected coordinates

**Usage:**

```bash
python camera_pos_calculator.py
```

### 2. DXF Vertex Reader (`dxf_vertex_reader.py`)

Advanced DXF file processor that extracts 3D vertex coordinates from polylines with geological analysis capabilities.

**Features:**

- Processes DXF VERTEX entities from polylines
- Removes duplicate vertices within polylines
- Filters to only process 3-vertex triangular faces
- Calculates geological dip and dip direction angles
- Computes triangle area measurements
- Advanced variance analysis using ±0.05 coordinate perturbations
- CSV output with natural sorting and precision control
- Comprehensive error handling and validation

**Requirements:**

- DXF file with VERTEX entities in polylines
- Python packages: `numpy`, `tkinter`

**Output:**

- CSV file with vertex coordinates and geological analysis (dip, dip direction, area, variance)

**Usage:**

```bash
python dxf_vertex_reader.py
```

### 3. RINEX OBS File Corrector (`rinex_obs_file_corrector.py`)

Corrects and reformats RINEX observation files to ensure proper formatting and RINEX standard compliance.

**Features:**

- Batch processing of all `.obs` files in directory
- Time format standardization
- Header corrections and proper spacing
- Automatic backup of original files

**Requirements:**

- `.obs` RINEX observation files
- Standard Python library (os, math)

**Output:**

- Corrected files with `_corrected.obs` suffix

**Usage:**

```bash
python rinex_obs_file_corrector.py
```

## Legacy Scripts (Old-Scripts/)

The `Old-Scripts/` directory contains previous versions of tools maintained for compatibility:

### DXF Point Reader (`dxf_file_point_reader.py`)

Legacy version that extracts 3D point coordinates from DXF POINT entities.

**Features:**

- Extracts all POINT entities from DXF files
- Simple coordinate extraction without geological analysis
- Formatted text output with point numbering

**Usage:**

```bash
python Old-Scripts/dxf_file_point_reader.py
```

### Pix4D Geological Analysis (`pix4d_3pt_face_dip_dipdir.py`)

Legacy geological analysis tool for Pix4D-generated DXF files.

**Features:**

- Processes grouped 3-point sets from Pix4D
- Basic dip and dip direction calculations
- Triangle area measurements

**Usage:**

```bash
python Old-Scripts/pix4d_3pt_face_dip_dipdir.py
```

## Installation

### Quick Start

For users who want to get started immediately:

```bash
# Clone the repository
git clone <repository-url>
cd drone-data-parser

# Install dependencies
pip install -r requirements.txt

# Run any script
python dxf_vertex_reader.py
```

### Prerequisites

- Python 3.10+ installed on your system
- Git (optional, for cloning)

### Setup Instructions

1. **Clone or download the repository**

   ```bash
   git clone <repository-url>
   cd drone-data-parser
   ```

   Or download and extract the ZIP file to your desired location.

2. **Create a virtual environment** (recommended)

   ```bash
   # Create virtual environment
   python -m venv drone-parser-env
   ```

3. **Activate the virtual environment**

   **On Windows:**

   ```bash
   # Command Prompt
   drone-parser-env\Scripts\activate

   # PowerShell
   drone-parser-env\Scripts\Activate.ps1

   # Git Bash
   source drone-parser-env/Scripts/activate
   ```

   **On macOS/Linux:**

   ```bash
   source drone-parser-env/bin/activate
   ```

4. **Install required packages**

   **Option A: Using requirements.txt (recommended)**

   ```bash
   pip install -r requirements.txt
   ```

### Running the Scripts

Once the virtual environment is activated and packages are installed, you can run any of the scripts:

```bash
python camera_pos_calculator.py
python dxf_vertex_reader.py
python rinex_obs_file_corrector.py

# Legacy scripts
python Old-Scripts/dxf_file_point_reader.py
python Old-Scripts/pix4d_3pt_face_dip_dipdir.py
```

## File Structure

```bash
drone-data-parser/
├── camera_pos_calculator.py             # Camera position calculator
├── dxf_vertex_reader.py                 # Advanced DXF vertex reader with geological analysis
├── rinex_obs_file_corrector.py          # RINEX file corrector
├── requirements.txt                     # Python dependencies
├── Old-Scripts/                         # Legacy scripts directory
│   ├── dxf_file_point_reader.py         # Legacy DXF point extractor
│   └── pix4d_3pt_face_dip_dipdir.py     # Legacy Pix4D geological analysis
└── README.md                            # This documentation
```

## Data Flow Examples

### Camera Position Processing

```bash
Image Files (*.jpg) + RINEX Data (*.pos) + Timestamps (*.MRK)
    → Camera_coords.csv
```

### DXF Vertex Reader

```bash
DXF File (VERTEX polylines) → 3-vertex filtering → Duplicate removal
    → Geological calculations (dip, dip direction, area)
    → Variance analysis (±0.05 coordinate perturbations)
    → CSV report with geological measurements
```

### RINEX Correction

```bash
Raw OBS files (*.obs) → Formatted files (*_corrected.obs)
```

### Legacy DXF Point Extraction (Superseded by DXF Vertex Reader)

```bash
DXF File (POINT entities) → Coordinate extraction → Text report
```

## Troubleshooting

### Installation Issues

1. **Python version errors**: Ensure you're using Python 3.10 or higher

   ```bash
   python --version
   ```

2. **Pip not found**: Make sure pip is installed and updated

   ```bash
   python -m ensurepip --upgrade
   python -m pip install --upgrade pip
   ```

3. **Virtual environment issues**: Recreate the virtual environment

   ```bash
   deactivate  # if already in a venv
   rm -rf drone-parser-env  # remove old environment
   python -m venv drone-parser-env
   # Reactivate and install
   ```

### Runtime Issues

1. **No files found**: Ensure input files are in the correct directory
2. **Import errors**: Verify all packages are installed correctly with `pip list`
3. **File format errors**: Verify input files follow expected formats
4. **Permission errors**: Ensure write permissions in output directory

### File Format Requirements

- **Image files**: Must follow naming pattern `prefix_prefix_ID.jpg`
- **DXF files**: Must contain POINT entities in standard DXF format
- **RINEX files**: Must be valid observation files with `.obs` extension

## Contributing

This project is maintained by Eric Tannant. For issues or improvements:

1. Ensure code follows PEP 8 style guidelines
2. Add appropriate type hints and docstrings
3. Include error handling for edge cases

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
