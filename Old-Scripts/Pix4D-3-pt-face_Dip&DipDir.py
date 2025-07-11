"""
Drone Data Parser - Dip and Dip Direction Calculator for 3-Point Faces

This module calculates geological dip and dip direction from three-point plane data
extracted from Pix4D DXF files. It processes POINT entities in DXF format and 
computes structural geology measurements.

Author: Eric Tannant
Created: August 2023
Updated: June 20205
Version: 1.5
License: MIT

Description:
    Reads DXF files containing 3D point data, groups them into sets of three points
    that define geological planes, and calculates the dip (inclination angle) and 
    dip direction (azimuth) of each plane. Results include point coordinates,
    dip/dip direction angles, and triangle area.

Requirements:
    - numpy
    - pandas
    - tkinter
    - DXF file with POINT entities

Output:
    - CSV file with point coordinates, dip, dip direction, and area data
"""

import re
import os
import sys
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
from typing import List, Tuple, Optional


class Point3D:
    """Represents a 3D point with x, y, z coordinates."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"


class GeologicalPlane:
    """Represents a plane defined by three points."""
    
    def __init__(self, point1: Point3D, point2: Point3D, point3: Point3D):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.dip = 0.0
        self.dip_direction = 0.0
        self.area = 0.0
        self._calculate_plane_properties()
    
    def _calculate_plane_properties(self):
        """Calculate dip, dip direction, and area of the plane."""
        # Create vectors from point1 to point2 and point1 to point3
        vector_a = np.array([
            self.point2.x - self.point1.x,
            self.point2.y - self.point1.y,
            self.point2.z - self.point1.z
        ])
        
        vector_b = np.array([
            self.point3.x - self.point1.x,
            self.point3.y - self.point1.y,
            self.point3.z - self.point1.z
        ])
        
        # Calculate cross product (normal vector)
        cross_product = np.cross(vector_a, vector_b)
        
        # Calculate area of triangle
        self.area = self._magnitude(cross_product) / 2.0
        
        # Calculate unit normal vector
        if self.area > 0:
            unit_normal = cross_product / (2.0 * self.area)
            
            # Ensure normal vector points upward (positive z component)
            if unit_normal[2] < 0:
                unit_normal = -unit_normal
            
            # Calculate dip (inclination from horizontal)
            self.dip = 90.0 - math.degrees(math.asin(abs(unit_normal[2])))
            
            # Calculate dip direction (azimuth)
            self.dip_direction = self._calculate_dip_direction(unit_normal[0], unit_normal[1])
    
    @staticmethod
    def _magnitude(vector: np.ndarray) -> float:
        """Calculate the magnitude of a vector."""
        return math.sqrt(sum(component**2 for component in vector))
    
    @staticmethod
    def _calculate_dip_direction(normal_x: float, normal_y: float) -> float:
        """
        Calculate dip direction from normal vector components.
        
        Args:
            nx: X component of unit normal vector
            ny: Y component of unit normal vector
            
        Returns:
            Dip direction in degrees (0-360)
        """
        if normal_x > 0 and normal_y > 0:
            return math.degrees(math.atan(normal_x / normal_y))
        elif normal_x < 0 and normal_y < 0:
            return 180.0 + math.degrees(math.atan(normal_x / normal_y))
        elif normal_x > 0 and normal_y < 0:
            return 180.0 + math.degrees(math.atan(normal_x / normal_y))
        elif normal_x < 0 and normal_y > 0:
            return 360.0 + math.degrees(math.atan(normal_x / normal_y))
        elif normal_x == 0:
            return 0.0 if normal_y > 0 else 180.0
        elif normal_y == 0:
            return 90.0 if normal_x > 0 else 270.0
        else:
            return 0.0


class DXFPointExtractor:
    """Extracts 3D points from DXF files."""
    
    def __init__(self):
        self.point_pattern = re.compile(r"POINT")
    
    def extract_points_from_dxf(self, file_path: str) -> List[Point3D]:
        """
        Extract all POINT entities from a DXF file.
        
        Args:
            file_path: Path to the DXF file
            
        Returns:
            List of Point3D objects
        """
        points = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                
            i = 0
            while i < len(lines):
                if self.point_pattern.search(lines[i]):
                    point = self._extract_single_point(lines, i)
                    if point:
                        points.append(point)
                i += 1
                
        except Exception as e:
            print(f"Error reading DXF file: {e}")
            return []
        
        return points
    
    def _extract_single_point(self, lines: List[str], start_index: int) -> Optional[Point3D]:
        """
        Extract a single point starting from a POINT line.
        
        Args:
            lines: All lines from the file
            start_index: Index of the POINT line
            
        Returns:
            Point3D object or None if extraction fails
        """
        try:
            # Skip to coordinate data (typically 12 lines after POINT)
            coord_start = start_index + 13  # Adjusted for typical DXF structure
            
            if coord_start + 5 >= len(lines):
                return None
            
            # Extract coordinates (assuming standard DXF structure)
            x_coord = float(lines[coord_start].strip())
            y_coord = float(lines[coord_start + 2].strip())
            z_coord = float(lines[coord_start + 4].strip())
            
            return Point3D(x_coord, y_coord, z_coord)
            
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not extract point at line {start_index}: {e}")
            return None


def select_input_file() -> Optional[str]:
    """
    Open a file dialog to select the input DXF file.
    
    Returns:
        Selected file path or None if cancelled
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select DXF file",
        filetypes=[
            ("DXF files", "*.dxf"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return file_path if file_path else None


def process_geological_planes(input_file_path: str) -> bool:
    """
    Process DXF file to calculate dip and dip direction for geological planes.
    
    Args:
        input_file_path: Path to the input DXF file
        
    Returns:
        True if processing successful, False otherwise
    """
    if not os.path.exists(input_file_path):
        print(f"Error: File not found: {input_file_path}")
        return False
    
    print(f"Processing file: {input_file_path}")
    
    # Extract points from DXF file
    extractor = DXFPointExtractor()
    points = extractor.extract_points_from_dxf(input_file_path)
    
    if len(points) < 3:
        print(f"Error: Need at least 3 points to define a plane. Found {len(points)} points.")
        return False
    
    print(f"Extracted {len(points)} points from DXF file")
    
    # Group points into sets of three and calculate plane properties
    planes = []
    for i in range(0, len(points) - 2, 3):
        if i + 2 < len(points):
            plane = GeologicalPlane(points[i], points[i + 1], points[i + 2])
            planes.append(plane)
    
    if not planes:
        print("Error: No valid planes could be created from the points.")
        return False
    
    print(f"Created {len(planes)} geological planes")
    
    # Create output file
    name, ext = os.path.splitext(input_file_path)
    output_file_path = f"{name}_geological_analysis.csv"
    
    try:
        with open(output_file_path, 'w', newline='') as output_file:
            # Write header
            output_file.write("Point1_X,Point1_Y,Point1_Z,Point2_X,Point2_Y,Point2_Z,Point3_X,Point3_Y,Point3_Z,Dip,Dip_Direction,Area\n")
            
            # Write data for each plane
            for i, plane in enumerate(planes):
                output_file.write(
                    f"{plane.point1.x:.6f},{plane.point1.y:.6f},{plane.point1.z:.6f},"
                    f"{plane.point2.x:.6f},{plane.point2.y:.6f},{plane.point2.z:.6f},"
                    f"{plane.point3.x:.6f},{plane.point3.y:.6f},{plane.point3.z:.6f},"
                    f"{plane.dip:.2f},{plane.dip_direction:.2f},{plane.area:.2f}\n"
                )
        
        print(f"Results written to: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    """Main function to run the geological plane analysis."""
    print("Dip and Dip Direction Calculator for 3-Point Faces")
    print("=" * 50)
    
    # Select input file
    input_file = select_input_file()
    if not input_file:
        print("No file selected. Exiting.")
        return
    
    # Process the file
    success = process_geological_planes(input_file)
    
    if success:
        print("\nProcessing completed successfully!")
    else:
        print("\nProcessing failed. Please check the input file and try again.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
