# Drone Data Parser

A comprehensive toolkit for processing and analyzing drone survey data, including camera positioning, geological measurements, and RINEX observation file correction.

## Author

**Eric Tannant**
Originally created: 2023
Updated: July 2025
Version: 1.1
License: MIT

## Overview

This project contains four specialized modules for drone data processing:

1. **Camera Position Calculator** - Correlates drone images with GPS coordinates
2. **DXF Point Reader** - Extracts 3D coordinates from CAD files
3. **Geological Plane Analysis** - Calculates dip and dip direction from 3-point data
4. **RINEX OBS File Corrector** - Fixes formatting issues in GPS observation files

## Modules

### 1. Camera Position Calculator (`CameraPosCalculator.py`)

Calculates accurate camera positions for drone images by correlating timestamp data with RINEX GPS positioning data.

**Features:**

- Processes JPG/jpg files with structured naming convention
- Interpolates GPS positions based on image timestamps
- Applies offset corrections for precise positioning
- Handles day boundary crossings in GPS data

**Requirements:**

- JPG/jpg image files (format: `prefix_prefix_ID.jpg`)
- `.pos` RINEX positioning file
- `.MRK` timestamp file
- Python packages: `pandas`

**Output:**

- `Camera_coords.txt` - CSV file with image names and corrected coordinates

**Usage:**

```bash
python CameraPosCalculator.py
```

### 2. DXF Point Reader (`DXF-File-Point-Reader.py`)

Extracts 3D point coordinates from DXF (Drawing Exchange Format) files.

**Features:**

- GUI file selection dialog
- Extracts all POINT entities from DXF files
- Formatted output with point numbering
- Error handling for corrupt or invalid files

**Requirements:**

- DXF file with POINT entities
- Python packages: `tkinter`

**Output:**

- Text file with extracted coordinates in X, Y, Z format

**Usage:**

```bash
python DXF-File-Point-Reader.py
```

### 3. Geological Plane Analysis (`Pix4D-3-pt-face_Dip&DipDir.py`)

Calculates geological dip and dip direction from three-point plane data extracted from Pix4D DXF files.

**Features:**

- Object-oriented design with Point3D and GeologicalPlane classes
- Automatic calculation of dip, dip direction, and triangle area
- Proper handling of normal vector orientation
- CSV output with comprehensive data

**Requirements:**

- DXF file with grouped sets of 3 points defining geological planes
- Python packages: `numpy`, `tkinter`

**Output:**

- CSV file with point coordinates, dip, dip direction, and area measurements

**Usage:**

```bash
python Pix4D-3-pt-face_Dip&DipDir.py
```

### 4. RINEX OBS File Corrector (`RINEX-OBS-File-Corrector.py`)

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

- Corrected files with `_corrected.txt` suffix

**Usage:**

```bash
python RINEX-OBS-File-Corrector.py
```

## Installation

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

   ```bash
   pip install pandas numpy
   ```

5. **Verify installation**

   ```bash
   python -c "import pandas, numpy; print('All packages installed successfully!')"
   ```

### Running the Scripts

Once the virtual environment is activated and packages are installed, you can run any of the scripts:

```bash
python CameraPosCalculator.py
python DXF-File-Point-Reader.py
python Pix4D-3-pt-face_Dip&DipDir.py
python RINEX-OBS-File-Corrector.py
```

### Deactivating the Virtual Environment

When you're done working with the project, deactivate the virtual environment:

```bash
deactivate
```

### Alternative: Requirements File

For easier dependency management, you can create a `requirements.txt` file:

```bash
# Create requirements.txt
echo "pandas>=1.3.0" > requirements.txt
echo "numpy>=1.20.0" >> requirements.txt

# Install from requirements file
pip install -r requirements.txt
```

## File Structure

```
drone-data-parser/
├── CameraPosCalculator.py              # Camera position calculator
├── DXF-File-Point-Reader.py            # DXF coordinate extractor
├── Pix4D-3-pt-face_Dip&DipDir.py       # Geological analysis
├── RINEX-OBS-File-Corrector.py         # RINEX file corrector
└── README.md                           # This documentation
```

## Data Flow Examples

### Camera Position Processing

```
Image Files (*.jpg) + RINEX Data (*.pos) + Timestamps (*.MRK)
    → Camera_coords.txt
```

### Geological Analysis

```
DXF File (3-point sets) → Geological measurements → CSV report
```

### RINEX Correction

```
Raw OBS files (*.obs) → Formatted files (*_corrected.txt)
```

## Troubleshooting

### Common Issues

1. **No files found**: Ensure input files are in the correct directory
2. **Import errors**: Install required packages with pip
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

MIT License - see individual file headers for details.
