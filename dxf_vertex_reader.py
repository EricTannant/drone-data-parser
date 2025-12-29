"""
Drone Data Parser - DXF Vertex Reader

This module extracts 3D vertex coordinates from DXF files.
It searches for VERTEX entities grouped by polylines and writes their coordinates
to a text file, organized by polyline.

Author: Eric Tannant
Created: June 2025
Updated: August 2025
Version: 1.1
License: MIT

Description:
    Reads DXF files and extracts all VERTEX entity coordinates grouped by polylines.
    The script processes the DXF file structure to locate and parse 3D coordinate data,
    then exports the results to a formatted text file organized by polyline.
    Only polylines with exactly 3 vertices are included in the output.
    Duplicate vertices within the same polyline are automatically removed.
    Geological analysis (dip, dip direction, and area) is calculated for each valid polyline.

Requirements:
    - tkinter (for file dialog)
    - numpy (for geological calculations)
    - DXF file with VERTEX entities organized in polylines

Output:
    - CSV file with extracted vertex coordinates grouped by polyline (X, Y, Z)
    - Geological analysis (dip, dip direction, and area) included in the same CSV file
    - Data is properly sorted by polyline number (natural order: 1, 2, 3, ... 10, 11, etc.)
"""

import itertools
import math
import os
import re
import sys
from typing import Dict, List, Optional

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox


class Vertex3D:
    """Represents a 3D vertex with coordinates."""

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"{self.x:.6f}, {self.y:.6f}, {self.z:.6f}"

    def __repr__(self):
        return f"Vertex3D({self.x}, {self.y}, {self.z})"

    def __eq__(self, other):
        """Check if two vertices are equal (for duplicate detection)."""
        if not isinstance(other, Vertex3D):
            return False
        tolerance = 1e-6
        return (abs(self.x - other.x) < tolerance and
                abs(self.y - other.y) < tolerance and
                abs(self.z - other.z) < tolerance)

    def __hash__(self):
        """Make vertices hashable for use in sets."""
        # Round to avoid floating point precision issues
        return hash((round(self.x, 6), round(self.y, 6), round(self.z, 6)))


class Polyline:
    """Represents a polyline with its vertices."""

    def __init__(self, name: str):
        self.name = name
        self.vertices = []
        self.dip = 0.0
        self.dip_direction = 0.0
        self.area = 0.0
        self.length_sum = 0.0
        self.dip_variance = 0.0
        self.dip_direction_variance = 0.0

    def add_vertex(self, vertex: Vertex3D):
        """Add a vertex to this polyline if it's not a duplicate.

        This is to remove accidental missclicks.
        """
        # Check for duplicates
        for existing_vertex in self.vertices:
            if vertex == existing_vertex:
                print(f"Warning: Duplicate vertex found in {self.name}, skipping")
                return
        self.vertices.append(vertex)

    def vertex_count(self) -> int:
        """Return the number of vertices in this polyline."""
        return len(self.vertices)

    def is_valid(self) -> bool:
        """Check if polyline has exactly 3 vertices."""
        return len(self.vertices) == 3

    def calculate_geological_properties(self):
        """Calculate dip, dip direction, and area if polyline has exactly 3 vertices."""
        if not self.is_valid():
            return

        # Get the three vertices
        p1, p2, p3 = self.vertices[0], self.vertices[1], self.vertices[2]

        # Calculate main geological properties
        self.dip, self.dip_direction, self.area, self.length_sum = self._calculate_properties_for_points(p1, p2, p3)

        # Calculate variance using ±0.005 variations
        self._calculate_variance()

    def _calculate_properties_for_points(self, p1, p2, p3):
        """Calculate dip, dip direction, and area for given points."""
        # Create vectors from point1 to point2 and point1 to point3
        vector_a = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
        vector_b = np.array([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])

        # Calculate cross product (normal vector)
        cross_product = np.cross(vector_a, vector_b)

        # Calculate area of triangle
        triangle_area = self._magnitude(cross_product) / 2.0
        length_sum = self._magnitude(vector_a) + self._magnitude(vector_b)

        # Calculate unit normal vector
        if triangle_area > 0:
            unit_normal = cross_product / (2.0 * triangle_area)

            # Ensure normal vector points upward (positive z component)
            if unit_normal[2] < 0:
                unit_normal = -unit_normal

            # Calculate dip (inclination from horizontal)
            dip = 90.0 - math.degrees(math.asin(unit_normal[2]))

            # Calculate dip direction (azimuth)
            dip_direction = self._calculate_dip_direction(unit_normal[0], unit_normal[1])

            return dip, dip_direction, triangle_area, length_sum

        return 0.0, 0.0, 0.0, 0.0

    def _calculate_variance(self):
        """Calculate variance in dip and dip direction using ±0.005 coordinate variations."""
        if not self.is_valid():
            return

        variance = 0.005
        p1, p2, p3 = self.vertices[0], self.vertices[1], self.vertices[2]

        # Store all calculated dip and dip direction values
        dip_values = []
        dip_direction_values = []

        # Generate all possible combinations of ±variance for each coordinate
        variations = [-variance, variance]
        
        # Create all combinations using itertools.product (2^9 = 512 combinations)
        for deltas in itertools.product(variations, repeat=9):
            # Unpack deltas: 3 coordinates × 3 points = 9 values
            dx1, dy1, dz1, dx2, dy2, dz2, dx3, dy3, dz3 = deltas
            
            # Create varied points
            varied_points = self._create_varied_points(p1, p2, p3, dx1, dy1, dz1, 
                                                     dx2, dy2, dz2, dx3, dy3, dz3)
            
            # Calculate properties for varied points
            dip, dip_direction, _ = self._calculate_properties_for_points(*varied_points)
            
            if dip > 0:  # Valid calculation
                dip_values.append(dip)
                dip_direction_values.append(dip_direction)

        # Calculate variances
        if dip_values:
            self.dip_variance = max(dip_values) - min(dip_values)
            
            # Handle dip direction variance (accounting for circular nature of angles)
            self.dip_direction_variance = self._calculate_circular_variance(dip_direction_values)
        else:
            self.dip_variance = 0.0
            self.dip_direction_variance = 0.0

    def _create_varied_points(self, p1, p2, p3, dx1, dy1, dz1, dx2, dy2, dz2, dx3, dy3, dz3):
        """Create three varied points with given delta values."""
        varied_p1 = Vertex3D(p1.x + dx1, p1.y + dy1, p1.z + dz1)
        varied_p2 = Vertex3D(p2.x + dx2, p2.y + dy2, p2.z + dz2)
        varied_p3 = Vertex3D(p3.x + dx3, p3.y + dy3, p3.z + dz3)
        return varied_p1, varied_p2, varied_p3

    @staticmethod
    def _calculate_circular_variance(angles):
        """Calculate variance for circular data (angles)."""
        if not angles:
            return 0.0

        # First, check if we span across 0°/360° boundary
        min_angle = min(angles)
        max_angle = max(angles)

        # If the range is large, check if it's because we're crossing 0°/360°
        if max_angle - min_angle > 180:
            # Convert angles to handle the circular boundary
            adjusted_angles = []
            for angle in angles:
                if angle > 180:
                    adjusted_angles.append(angle - 360)
                else:
                    adjusted_angles.append(angle)

            # Recalculate with adjusted angles
            adjusted_min = min(adjusted_angles)
            adjusted_max = max(adjusted_angles)

            # Use the smaller range
            if abs(adjusted_max - adjusted_min) < abs(max_angle - min_angle):
                return adjusted_max - adjusted_min

        return max_angle - min_angle

    @staticmethod
    def _magnitude(vector: np.ndarray) -> float:
        """Calculate the magnitude of a vector."""
        return math.sqrt(sum(component**2 for component in vector))

    @staticmethod
    def _calculate_dip_direction(normal_x: float, normal_y: float) -> float:
        """Calculate dip direction from normal vector components.
        
        Returns azimuth in degrees from 0-360 degrees, where:
        - North = 0°
        - East = 90°
        - South = 180°
        - West = 270°
        """
        return (math.degrees(math.atan2(normal_x, normal_y))) % 360.0

    def __str__(self):
        return f"Polyline {self.name}: {len(self.vertices)} vertices"


class DXFVertexReader:
    """Reads and extracts 3D vertices from DXF files, grouped by polylines."""

    def __init__(self):
        self.vertex_pattern = re.compile(r"VERTEX")
        self.polylines = {}

    def read_dxf_file(self, file_path: str) -> Dict[str, Polyline]:
        """
        Read DXF file and extract all VERTEX entities grouped by polylines.

        Args:
            file_path: Path to the DXF file

        Returns:
            Dictionary of polyline names to Polyline objects

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DXF file not found: {file_path}")

        self.polylines = {}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()

            self._extract_vertices_from_lines(lines)

        except IOError as e:
            raise IOError(f"Error reading DXF file: {e}")

        return self.polylines

    def _extract_vertices_from_lines(self, lines: List[str]) -> None:
        """
        Extract vertices from DXF file lines and group them by polylines.

        Args:
            lines: List of all lines from the DXF file
        """
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if self.vertex_pattern.search(line):
                vertex_data = self._extract_single_vertex(lines, i)
                if vertex_data:
                    vertex, polyline_name = vertex_data

                    # Get or create polyline
                    if polyline_name not in self.polylines:
                        self.polylines[polyline_name] = Polyline(polyline_name)

                    self.polylines[polyline_name].add_vertex(vertex)
            i += 1

    def _extract_single_vertex(self, lines: List[str], start_index: int) -> Optional[tuple]:
        """
        Extract a single vertex and its polyline name from DXF lines starting at the VERTEX entity.

        Args:
            lines: All lines from the file
            start_index: Index where VERTEX was found

        Returns:
            Tuple of (Vertex3D object, polyline_name) or None if extraction fails
        """
        try:
            # Look for the polyline name in the entity section
            polyline_name = None
            x_coord = None
            y_coord = None
            z_coord = None

            # Search for polyline name and coordinates in the following lines
            search_limit = min(start_index + 20, len(lines))

            for j in range(start_index + 1, search_limit):
                line = lines[j].strip()

                # Look for layer name (group code 8) which contains the polyline name
                if j + 1 < len(lines) and line == "8":
                    layer_line = lines[j + 1].strip()
                    if layer_line.startswith("Polyline"):
                        polyline_name = layer_line

                # Look for X coordinate (group code 10)
                elif line == "10" and j + 1 < len(lines):
                    try:
                        x_coord = float(lines[j + 1].strip())
                    except ValueError:
                        continue

                # Look for Y coordinate (group code 20)
                elif line == "20" and j + 1 < len(lines):
                    try:
                        y_coord = float(lines[j + 1].strip())
                    except ValueError:
                        continue

                # Look for Z coordinate (group code 30)
                elif line == "30" and j + 1 < len(lines):
                    try:
                        z_coord = float(lines[j + 1].strip())
                    except ValueError:
                        continue

                # If we have all required data, create the vertex
                if all(v is not None for v in [polyline_name, x_coord, y_coord, z_coord]):
                    vertex = Vertex3D(x_coord, y_coord, z_coord)
                    return (vertex, polyline_name)

            return None

        except (ValueError, IndexError) as e:
            print(f"Warning: Could not extract vertex at line {start_index}: {e}")
            return None

    def get_valid_polylines(self) -> Dict[str, Polyline]:
        """
        Get only polylines that have exactly 3 vertices and calculate their geological properties.

        Returns:
            Dictionary of valid polylines
        """
        valid_polylines = {name: polyline for name, polyline in self.polylines.items()
                          if polyline.is_valid()}

        # Calculate geological properties for each valid polyline
        for polyline in valid_polylines.values():
            polyline.calculate_geological_properties()

        return valid_polylines


def natural_sort_key(polyline_name: str) -> List:
    """
    Generate a key for natural sorting of polyline names.
    Converts 'Polyline 10' to come after 'Polyline 2'.
    """
    import re
    parts = re.split(r'(\d+)', polyline_name)
    return [int(part) if part.isdigit() else part for part in parts]


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
        title="Save Vertex Coordinates As",
        defaultextension=".csv",
        filetypes=[
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )

    root.destroy()
    return file_path if file_path else None


def write_polylines_to_file(polylines: Dict[str, Polyline], output_path: str, source_file: str) -> bool:
    """
    Write extracted polylines and vertices to CSV output file.

    Args:
        polylines: Dictionary of polyline names to Polyline objects
        output_path: Path for output file
        source_file: Original DXF filename for reference

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as output_file:
            # Sort polylines by natural order (1, 2, 3, ... 10, 11, etc.)
            sorted_polylines = sorted(polylines.items(), key=lambda x: natural_sort_key(x[0]))

            # Write vertex coordinates section
            output_file.write(
                "Polyline,Vertex1_X,Vertex1_Y,Vertex1_Z,Vertex2_X,Vertex2_Y,"
                "Vertex2_Z,Vertex3_X,Vertex3_Y,Vertex3_Z\n"
            )

            for polyline_name, polyline in sorted_polylines:
                v1, v2, v3 = polyline.vertices[0], polyline.vertices[1], polyline.vertices[2]
                output_file.write(
                    f"{polyline_name},{v1.x:.2f},{v1.y:.2f},{v1.z:.2f},"
                    f"{v2.x:.2f},{v2.y:.2f},{v2.z:.2f},"
                    f"{v3.x:.2f},{v3.y:.2f},{v3.z:.2f}\n"
                )

            # Add vertical separator
            output_file.write("\n")

            # Write geological analysis section
            output_file.write("Polyline,Dip,Dip_Direction,Area,Trace,Dip_Variance,Dip_Direction_Variance\n")

            for polyline_name, polyline in sorted_polylines:
                output_file.write(
                    f"{polyline_name},{polyline.dip:.1f},{polyline.dip_direction:.1f},{polyline.area:.2f},"
                    f"{polyline.length_sum:.2f},{polyline.dip_variance:.1f},{polyline.dip_direction_variance:.1f}\n"
                )

        return True

    except IOError as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    """Main function to run the DXF vertex reader."""
    print("DXF Vertex Reader v1.0")
    print("=" * 35)

    # Select input file
    input_file = select_input_file()
    if not input_file:
        print("No input file selected. Exiting.")
        return

    print(f"Selected input file: {os.path.basename(input_file)}")

    # Create DXF reader and extract vertices
    reader = DXFVertexReader()

    try:
        all_polylines = reader.read_dxf_file(input_file)
        valid_polylines = reader.get_valid_polylines()

        if not valid_polylines:
            print("No valid polylines found (polylines must have exactly 3 vertices).")
            messagebox.showwarning("No Valid Polylines",
                                 "No polylines with exactly 3 vertices were found in the selected DXF file.")
            return

        total_vertices = sum(len(polyline.vertices) for polyline in valid_polylines.values())
        ignored_polylines = len(all_polylines) - len(valid_polylines)

        print(f"Successfully extracted {len(valid_polylines)} valid polylines")
        print(f"Total vertices: {total_vertices}")
        if ignored_polylines > 0:
            print(f"Ignored {ignored_polylines} polylines without exactly 3 vertices")

        # Select output file
        default_output_name = os.path.splitext(os.path.basename(input_file))[0] + "_vertices.csv"
        output_file = select_output_file(default_output_name)

        if not output_file:
            print("No output file selected. Exiting.")
            return

        # Write results
        if write_polylines_to_file(valid_polylines, output_file, input_file):
            print(f"Results written to: {output_file}")

            summary_msg = (f"Vertex extraction and geological analysis completed!\n\n"
                          f"Found {len(valid_polylines)} valid polylines\n"
                          f"Total vertices: {total_vertices}")

            if ignored_polylines > 0:
                summary_msg += f"\nIgnored {ignored_polylines} polylines without exactly 3 vertices"

            summary_msg += f"\n\nResults saved to:\n{output_file}"

            messagebox.showinfo("Success", summary_msg)
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
