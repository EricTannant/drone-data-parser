"""
Drone Data Parser - DXF Point Reader

This module extracts 3D point coordinates from DXF (Drawing Exchange Format) files.
It searches for POINT entities and writes their coordinates to a text file.

Author: Eric Tannant
Created: August 2021
Updated: June 2025
Version: 1.7
License: MIT

Description:
    Reads DXF files and extracts all POINT entity coordinates. The script processes
    the DXF file structure to locate and parse 3D coordinate data, then exports
    the results to a formatted text file.

Requirements:
    - tkinter (for file dialog)
    - DXF file with POINT entities

Output:
    - Text file with extracted point coordinates (X, Y, Z)
"""

import re
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple, Optional


class Point3D:
    """Represents a 3D point with coordinates."""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"{self.x:.6f}, {self.y:.6f}, {self.z:.6f}"
    
    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"


class DXFPointReader:
    """Reads and extracts 3D points from DXF files."""
    
    def __init__(self):
        self.point_pattern = re.compile(r"POINT")
        self.points = []
    
    def read_dxf_file(self, file_path: str) -> List[Point3D]:
        """
        Read DXF file and extract all POINT entities.
        
        Args:
            file_path: Path to the DXF file
            
        Returns:
            List of Point3D objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DXF file not found: {file_path}")
        
        self.points = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                
            self._extract_points_from_lines(lines)
            
        except IOError as e:
            raise IOError(f"Error reading DXF file: {e}")
        
        return self.points
    
    def _extract_points_from_lines(self, lines: List[str]) -> None:
        """
        Extract points from DXF file lines.
        
        Args:
            lines: List of all lines from the DXF file
        """
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if self.point_pattern.search(line):
                point = self._extract_single_point(lines, i)
                if point:
                    self.points.append(point)
            i += 1
    
    def _extract_single_point(self, lines: List[str], start_index: int) -> Optional[Point3D]:
        """
        Extract a single point from DXF lines starting at the POINT entity.
        
        Args:
            lines: All lines from the file
            start_index: Index where POINT was found
            
        Returns:
            Point3D object or None if extraction fails
        """
        try:
            # DXF format: skip to coordinate data (typically 12 lines after POINT)
            coord_index = start_index + 13
            
            if coord_index + 5 >= len(lines):
                return None
            
            # Extract X, Y, Z coordinates
            x_coord = float(lines[coord_index].strip())
            # Skip 2 lines to next coordinate
            y_coord = float(lines[coord_index + 2].strip())
            # Skip 2 more lines to next coordinate
            z_coord = float(lines[coord_index + 4].strip())
            
            return Point3D(x_coord, y_coord, z_coord)
            
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not extract point at line {start_index}: {e}")
            return None


def select_input_file() -> Optional[str]:
    """
    Open file dialog to select DXF input file.
    
    Returns:
        Selected file path or None if cancelled
    """
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select DXF File",
        filetypes=[
            ("DXF files", "*.dxf"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return file_path if file_path else None


def select_output_file(default_name: str) -> Optional[str]:
    """
    Open file dialog to select output file location.
    
    Args:
        default_name: Default filename for output
        
    Returns:
        Selected file path or None if cancelled
    """
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.asksaveasfilename(
        title="Save Point Coordinates As",
        defaultextension=".txt",
        filetypes=[
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return file_path if file_path else None


def write_points_to_file(points: List[Point3D], output_path: str, source_file: str) -> bool:
    """
    Write extracted points to output file.
    
    Args:
        points: List of Point3D objects to write
        output_path: Path for output file
        source_file: Original DXF filename for reference
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as output_file:
            # Write header
            output_file.write(f"3D Point Coordinates extracted from: {os.path.basename(source_file)}\n")
            output_file.write(f"Total points found: {len(points)}\n")
            output_file.write("=" * 60 + "\n")
            output_file.write("Format: X, Y, Z\n")
            output_file.write("-" * 60 + "\n\n")
            
            # Write coordinates
            for i, point in enumerate(points, 1):
                output_file.write(f"Point {i:4d}: {point}\n")
            
            # Write footer
            output_file.write("\n" + "=" * 60 + "\n")
            output_file.write(f"End of coordinates for file: {os.path.basename(source_file)}\n")
        
        return True
        
    except IOError as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    """Main function to run the DXF point reader."""
    print("DXF Point Reader v2.0")
    print("=" * 30)
    
    # Select input file
    input_file = select_input_file()
    if not input_file:
        print("No input file selected. Exiting.")
        return
    
    print(f"Selected input file: {os.path.basename(input_file)}")
    
    # Create DXF reader and extract points
    reader = DXFPointReader()
    
    try:
        points = reader.read_dxf_file(input_file)
        
        if not points:
            print("No points found in the DXF file.")
            messagebox.showwarning("No Points", "No POINT entities were found in the selected DXF file.")
            return
        
        print(f"Successfully extracted {len(points)} points")
        
        # Select output file
        default_output_name = os.path.splitext(os.path.basename(input_file))[0] + "_points.txt"
        output_file = select_output_file(default_output_name)
        
        if not output_file:
            print("No output file selected. Exiting.")
            return
        
        # Write results
        if write_points_to_file(points, output_file, input_file):
            print(f"Results written to: {output_file}")
            messagebox.showinfo("Success", f"Point extraction completed!\n\nFound {len(points)} points.\nResults saved to:\n{output_file}")
        else:
            messagebox.showerror("Error", "Failed to write output file.")
            
    except Exception as e:
        error_msg = f"Error processing DXF file: {e}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)