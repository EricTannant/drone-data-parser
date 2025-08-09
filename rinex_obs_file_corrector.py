"""
Drone Data Parser - RINEX OBS File Corrector

This module corrects and reformats RINEX observation (.obs) files to ensure
proper formatting and compliance with RINEX standards. It processes all .obs
files in the current directory and creates corrected versions.

Author: Eric Tannant
Created: December 2023
Updated: August 2025
Version: 1.2
License: MIT

Description:
    Processes RINEX observation files to fix common formatting issues including:
    - Time format standardization
    - Header corrections
    - Proper spacing and alignment
    - Removal of problematic entries
    - Addition of required RINEX fields

Requirements:
    - Standard Python library (os, math)
    - .obs files in the current directory

Output:
    - Corrected .obs files with "_corrected.obs" suffix
"""

import math
import os
import sys
from typing import List, Optional, Tuple


class RinexObsCorrector:
    """Handles correction and reformatting of RINEX observation files."""

    def __init__(self):
        self.processed_files = 0
        self.errors = []

    def find_obs_files(self, directory: Optional[str] = None) -> List[str]:
        """
        Find all .obs files in the specified directory.

        Args:
            directory: Directory to search (defaults to current directory)

        Returns:
            List of .obs filenames
        """
        if directory is None:
            directory = os.getcwd()

        obs_files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith('.obs')
        ]

        return obs_files

    def format_time_component(self, component: str) -> str:
        """
        Format time component to ensure proper spacing.

        Args:
            component: Time component string

        Returns:
            Properly formatted time component
        """
        component = component.strip()
        if len(component) == 1:
            return ' ' + component
        return component

    def format_second_component(self, second_str: str) -> str:
        """
        Format seconds component for RINEX format.

        Args:
            second_str: Seconds string (may include decimal)

        Returns:
            Properly formatted seconds string
        """
        second_str = second_str.strip()
        if len(second_str) > 1 and second_str[1] == '.':
            return ' ' + second_str
        return second_str

    def parse_time_line(self, line: str) -> Tuple[List[str], str]:
        """
        Parse a time line and format it properly.

        Args:
            line: Raw time line from RINEX file

        Returns:
            Tuple of (formatted_components, formatted_line)
        """
        components = line.split()

        if len(components) < 9:
            raise ValueError(f"Invalid time line format: {line}")

        # Format each time component
        for i in range(2, 6):  # Month, day, hour, minute
            components[i] = self.format_time_component(components[i])

        # Format seconds component
        components[6] = self.format_second_component(components[6])

        # Format remaining components
        for i in range(7, 9):
            components[i] = self.format_time_component(components[i])

        # Reconstruct the line with proper spacing
        formatted_line = (
            f"> {components[1]} {components[2]} {components[3]} "
            f"{components[4]} {components[5]} {components[6]} "
            f"{components[7]} {components[8]}\n"
        )

        return components, formatted_line

    def create_header_lines(self, time_components: List[str]) -> Tuple[str, str]:
        """
        Create properly formatted header lines.

        Args:
            time_components: Parsed time components

        Returns:
            Tuple of (program_line, time_line)
        """
        # Ensure components are zero-padded for header
        padded_components = time_components.copy()
        for i in range(2, 6):  # Month, day, hour, minute
            if len(padded_components[i].strip()) == 1:
                padded_components[i] = '0' + padded_components[i].strip()

        # Handle seconds - take integer part and zero-pad
        seconds_int = str(math.floor(float(padded_components[6])))
        if len(seconds_int) == 1:
            seconds_int = '0' + seconds_int
        padded_components[6] = seconds_int

        # Create header lines
        program_line = (
            f"RTKCONV 2.4.3 b29                       "
            f"{padded_components[1]}{padded_components[2]}{padded_components[3]} "
            f"{padded_components[4]}{padded_components[5]}{padded_components[6]} "
            f"UTC PGM / RUN BY / DATE\n"
        )

        time_line = (
            f"  {padded_components[1]}    {padded_components[2]}    "
            f"{padded_components[3]}    {padded_components[4]}    "
            f"{padded_components[5]}   {padded_components[6]}     "
            f"GPS         TIME OF FIRST OBS\n"
        )

        return program_line, time_line

    def process_obs_file(self, filename: str) -> bool:
        """
        Process a single RINEX observation file.

        Args:
            filename: Name of the .obs file to process

        Returns:
            True if processing successful, False otherwise
        """
        try:
            print(f"Processing: {filename}")

            # Create output filename
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_corrected.obs"
            temp_filename = "temp_rinex_processing.obs"

            # First pass: process the file and handle time formatting
            time_components = None
            header_lines = None
            flag = 0  # Track which time instance we're processing

            with open(filename, 'r', encoding='utf-8', errors='ignore') as input_file:
                with open(output_filename, 'w') as output_file:

                    for line in input_file:
                        if line.startswith('>'):
                            flag += 1

                            if flag == 1:
                                # Skip the first time instance
                                continue
                            elif flag == 2:
                                # Process the second time instance
                                time_components, formatted_line = self.parse_time_line(line)
                                header_lines = self.create_header_lines(time_components)
                                # Don't write this line, store it for header generation
                                continue

                        # Write all other lines
                        output_file.write(line)

            if not time_components or not header_lines:
                raise ValueError("Could not find proper time information in file")

            # Second pass: fix headers and add proper formatting
            with open(output_filename, 'r') as temp_input:
                with open(temp_filename, 'w') as temp_output:

                    interval_line = "                                                            0.2000 INTERVAL     \n"

                    for line in temp_input:
                        line_stripped = line.strip()

                        # Skip empty lines and end marker
                        if not line_stripped or line_stripped == 'END OF RINEX OBS DATA':
                            continue

                        # Replace specific header lines
                        if 'UTC PGM / RUN BY' in line:
                            temp_output.write(header_lines[0])
                        elif 'TIME OF FIRST OBS' in line:
                            temp_output.write(interval_line)
                            temp_output.write(header_lines[1])
                        else:
                            temp_output.write(line)

                    # Add final space
                    temp_output.write(' ')

            # Replace original output with corrected version
            os.remove(output_filename)
            os.rename(temp_filename, output_filename)

            print(f"  → Created: {output_filename}")
            return True

        except Exception as e:
            error_msg = f"Error processing {filename}: {e}"
            print(f"  → Error: {error_msg}")
            self.errors.append(error_msg)

            # Clean up temporary files
            for temp_file in [output_filename, temp_filename]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

            return False

    def process_all_files(self, directory: Optional[str] = None) -> int:
        """
        Process all .obs files in the specified directory.

        Args:
            directory: Directory to process (defaults to current directory)

        Returns:
            Number of successfully processed files
        """
        obs_files = self.find_obs_files(directory)

        if not obs_files:
            print("No .obs files found in the directory.")
            return 0

        print(f"Found {len(obs_files)} .obs file(s) to process")
        print("-" * 50)

        successful_count = 0

        for filename in obs_files:
            if self.process_obs_file(filename):
                successful_count += 1

        return successful_count

    def print_summary(self, successful_count: int, total_count: int):
        """
        Print processing summary.

        Args:
            successful_count: Number of successfully processed files
            total_count: Total number of files attempted
        """
        print("\n" + "=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Files processed successfully: {successful_count}/{total_count}")

        if self.errors:
            print(f"\nErrors encountered:")
            for error in self.errors:
                print(f"  • {error}")

        if successful_count > 0:
            print(f"\nCorrected files can be found in the same folder with '_corrected.obs' suffix.")

        print("=" * 50)


def main():
    """Main function to run the RINEX OBS file corrector."""
    print("RINEX OBS File Corrector v2.0")
    print("=" * 40)
    print(f"Processing directory: {os.getcwd()}")
    print()

    corrector = RinexObsCorrector()

    try:
        obs_files = corrector.find_obs_files()
        successful_count = corrector.process_all_files()
        corrector.print_summary(successful_count, len(obs_files))

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()