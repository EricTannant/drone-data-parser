"""
Drone Data Parser - Camera Position Calculator

This module calculates accurate camera positions for drone images by correlating
timestamp data from .MRK files with RINEX GPS positioning data from .pos files.

Author: Eric Tannant
Created: August 2023
Updated: June 2025
Version: 1.6
License: MIT

Description:
    Processes JPG files in the current directory and matches them with GPS coordinates
    from RINEX positioning files. The script interpolates GPS positions based on
    image timestamps and applies offset corrections.

Requirements:
    - pandas
    - JPG/jpg image files in the script directory
    - .pos RINEX file
    - .MRK timestamp file

Output:
    - Camera_coords.txt: CSV file with image names and corrected coordinates
"""

import pandas as pd
import os
import sys
from typing import List, Tuple, Optional


def extract_image_id_from_filename(filename: str) -> Optional[int]:
    """
    Extract ID number from image filename.
    
    Expected format: prefix_prefix_ID.jpg
    
    Args:
        filename: Image filename
        
    Returns:
        ID number or None if extraction fails
    """
    try:
        parts = filename.split('_')
        if len(parts) >= 3:
            id_part = parts[2].split('.')[0]
            return int(id_part)
    except (ValueError, IndexError):
        pass
    return None


def process_rinex_data(rinex_file_path: str) -> List[List[float]]:
    """
    Process RINEX positioning data.
    
    Args:
        rinex_file_path: Path to the .pos file
        
    Returns:
        List of processed RINEX data [seconds, hours, east, north, elevation]
    """
    try:
        rinex_data = pd.read_csv(rinex_file_path, skiprows=5, delimiter=r"\s+")
        rinex_length = len(rinex_data)
        rinex_processed = []

        for i in range(rinex_length):
            hms_str = rinex_data.iloc[i, 5]
            hms_parts = hms_str.split(':')
            hms_values = list(map(float, hms_parts))
            hours, minutes, seconds = hms_values
            total_seconds = hours * 3600.0 + minutes * 60.0 + seconds
            hours_decimal = total_seconds / 3600.0
            
            rinex_processed.append([
                total_seconds,
                hours_decimal,
                rinex_data.iloc[i, 24],  # East
                rinex_data.iloc[i, 25],  # North
                rinex_data.iloc[i, 33]   # Elevation
            ])

        # Handle day boundary crossings
        for t in range(1, rinex_length):
            current_time = rinex_processed[t][1]
            past_time = rinex_processed[t - 1][1]
            if current_time - past_time <= 0:
                for i in range(t, rinex_length):
                    rinex_processed[i][1] += 24.0
                break

        return rinex_processed
    except Exception as e:
        print(f"Error processing RINEX data: {e}")
        return []


def process_timestamp_data(timestamp_file_path: str) -> Tuple[List[float], List[int], List[List[float]]]:
    """
    Process timestamp data from .MRK file.
    
    Args:
        timestamp_file_path: Path to the .MRK file
        
    Returns:
        Tuple of (image_times, image_ids, offsets)
    """
    try:
        timestamp_data = pd.read_csv(timestamp_file_path, header=None, sep='\t')
        num_photos = len(timestamp_data)
        
        image_times = []
        image_ids = []
        offsets = []

        for i in range(num_photos):
            image_id = timestamp_data.iloc[i, 0]
            image_ids.append(image_id)
            
            seconds = timestamp_data.iloc[i, 1]
            image_time = (seconds / 3600.0) - int(seconds / 3600.0 / 24.0) * 24.0
            image_times.append(image_time)
            
            # Parse coordinate offsets
            east_str = timestamp_data.iloc[i, 4].split(',')[0]
            north_str = timestamp_data.iloc[i, 3].split(',')[0]
            elev_str = timestamp_data.iloc[i, 5].split(',')[0]
            
            east_offset = float(east_str)
            north_offset = float(north_str)
            elev_offset = float(elev_str)
            
            offsets.append([east_offset, north_offset, elev_offset])

        # Handle day boundary crossings
        for t in range(1, num_photos):
            if image_times[t] - image_times[t - 1] < 0:
                for i in range(t, num_photos):
                    image_times[i] += 24
                break

        return image_times, image_ids, offsets
    except Exception as e:
        print(f"Error processing timestamp data: {e}")
        return [], [], []


def interpolate_coordinates(hour: float, rinex_data: List[List[float]], offset: List[float]) -> Tuple[float, float, float]:
    """
    Interpolate GPS coordinates for a given time.
    
    Args:
        hour: Time in decimal hours
        rinex_data: Processed RINEX data
        offset: [east_offset, north_offset, elev_offset] in mm
        
    Returns:
        Tuple of (east, north, elevation) coordinates
    """
    east_offset, north_offset, elev_offset = offset
    
    for i in range(1, len(rinex_data)):
        time_before = rinex_data[i - 1][1]
        time_after = rinex_data[i][1]
        
        if time_before < hour < time_after:
            # Linear interpolation
            delta_time_total = time_after - time_before
            delta_time_partial = hour - time_before
            weight = delta_time_partial / delta_time_total
            
            east_coord = rinex_data[i - 1][2] + (rinex_data[i][2] - rinex_data[i - 1][2]) * weight
            north_coord = rinex_data[i - 1][3] + (rinex_data[i][3] - rinex_data[i - 1][3]) * weight
            elev_coord = rinex_data[i - 1][4] + (rinex_data[i][4] - rinex_data[i - 1][4]) * weight
            
            # Apply offsets (convert mm to km)
            east_coord += east_offset / 1000.0
            north_coord += north_offset / 1000.0
            elev_coord -= elev_offset / 1000.0
            
            return east_coord, north_coord, elev_coord
        elif time_before == hour:
            # Exact match
            east_coord = rinex_data[i - 1][2] + east_offset / 1000.0
            north_coord = rinex_data[i - 1][3] + north_offset / 1000.0
            elev_coord = rinex_data[i - 1][4] - elev_offset / 1000.0
            return east_coord, north_coord, elev_coord
    
    raise ValueError(f"Time {hour} not found in RINEX data range")


def camera_position_calculator():
    """
    Main function to calculate camera positions for drone images.
    
    Processes JPG files, RINEX positioning data, and timestamp files to generate
    accurate camera coordinates for each image.
    """
    # Print header
    print("=" * 60)
    print("DRONE DATA PARSER - Camera Position Calculator")
    print("=" * 60)
    print(f"Version: 1.6 | Author: Eric Tannant")
    print()
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {script_directory}")
    print()

    # Find image files
    print("Searching for image files...")
    image_extensions = (".JPG", ".jpg")
    image_files = [
        f for f in os.listdir(script_directory) 
        if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(image_extensions)
    ]
    
    if not image_files:
        print("ERROR: No JPG/jpg files found in the directory.")
        print("       Please ensure image files are in the same directory as this script.")
        return False

    print(f"SUCCESS: Found {len(image_files)} image files")
    for i, img in enumerate(image_files[:5], 1):  # Show first 5 files
        print(f"         {i}. {img}")
    if len(image_files) > 5:
        print(f"         ... and {len(image_files) - 5} more files")
    print()

    # Extract image IDs
    print("Extracting image IDs from filenames...")
    image_ids_from_files = []
    valid_image_files = []
    invalid_files = []
    
    for image_file in image_files:
        image_id = extract_image_id_from_filename(image_file)
        if image_id is not None:
            image_ids_from_files.append(image_id)
            valid_image_files.append(image_file)
        else:
            invalid_files.append(image_file)

    if valid_image_files:
        print(f"SUCCESS: Successfully extracted IDs from {len(valid_image_files)} files")
        print(f"         ID range: {min(image_ids_from_files)} - {max(image_ids_from_files)}")
    
    if invalid_files:
        print(f"WARNING: Could not extract ID from {len(invalid_files)} files:")
        for invalid_file in invalid_files[:3]:  # Show first 3 invalid files
            print(f"         - {invalid_file}")
        if len(invalid_files) > 3:
            print(f"         ... and {len(invalid_files) - 3} more files")

    if not valid_image_files:
        print("ERROR: No valid image files with extractable IDs found.")
        print("       Expected filename format: prefix_prefix_ID.jpg")
        return False
    print()

    # Find and process RINEX file
    print("Processing RINEX positioning data...")
    rinex_files = [
        f for f in os.listdir(script_directory) 
        if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(".pos")
    ]
    
    if not rinex_files:
        print("ERROR: No .pos (RINEX) file found in the directory.")
        print("       Please ensure a RINEX positioning file (.pos) is in the same directory.")
        return False

    rinex_file_path = os.path.join(script_directory, rinex_files[0])
    print(f"Found RINEX file: {rinex_files[0]}")
    
    if len(rinex_files) > 1:
        print(f"NOTE: Multiple .pos files found, using: {rinex_files[0]}")
    
    print("Processing RINEX data...")
    rinex_data = process_rinex_data(rinex_file_path)
    if not rinex_data:
        print("ERROR: Failed to process RINEX data.")
        print("       Please check if the RINEX file is properly formatted.")
        return False
    
    print(f"SUCCESS: Successfully processed {len(rinex_data)} RINEX data points")
    print()

    # Find and process timestamp file
    print("Processing timestamp data...")
    timestamp_files = [
        f for f in os.listdir(script_directory) 
        if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(".MRK")
    ]
    
    if not timestamp_files:
        print("ERROR: No .MRK (timestamp) file found in the directory.")
        print("       Please ensure a timestamp file (.MRK) is in the same directory.")
        return False

    timestamp_file_path = os.path.join(script_directory, timestamp_files[0])
    print(f"Found timestamp file: {timestamp_files[0]}")
    
    if len(timestamp_files) > 1:
        print(f"NOTE: Multiple .MRK files found, using: {timestamp_files[0]}")
    
    print("Processing timestamp data...")
    image_times, image_ids, offsets = process_timestamp_data(timestamp_file_path)
    if not image_times:
        print("ERROR: Failed to process timestamp data.")
        print("       Please check if the timestamp file is properly formatted.")
        return False
    
    print(f"SUCCESS: Successfully processed {len(image_times)} timestamp entries")
    print()

    # Calculate coordinates for each valid image
    print("Calculating camera positions...")
    output_data = []
    matched_count = 0
    unmatched_images = []
    
    print(f"Processing {len(valid_image_files)} images...")
    
    for i, image_file in enumerate(valid_image_files):
        image_id = image_ids_from_files[i]
        
        # Show progress for large datasets
        if len(valid_image_files) > 10 and (i + 1) % max(1, len(valid_image_files) // 10) == 0:
            progress = (i + 1) / len(valid_image_files) * 100
            print(f"Progress: {progress:.0f}% ({i + 1}/{len(valid_image_files)} images)")
        
        # Find matching timestamp data
        try:
            timestamp_index = image_ids.index(image_id)
            hour = image_times[timestamp_index]
            offset = offsets[timestamp_index]
            
            east, north, elev = interpolate_coordinates(hour, rinex_data, offset)
            output_data.append([image_file, east, north, elev])
            matched_count += 1
            
        except (ValueError, IndexError):
            unmatched_images.append((image_file, image_id))

    if matched_count > 0:
        print(f"SUCCESS: Successfully calculated positions for {matched_count} images")
    
    if unmatched_images:
        print(f"WARNING: {len(unmatched_images)} images could not be matched:")
        for img_file, img_id in unmatched_images[:3]:  # Show first 3 unmatched
            print(f"         - {img_file} (ID: {img_id})")
        if len(unmatched_images) > 3:
            print(f"         ... and {len(unmatched_images) - 3} more images")

    if not output_data:
        print("ERROR: No images could be matched with timestamp data.")
        print("       Please check that image IDs match timestamp file entries.")
        return False
    print()

    # Write output file
    print("Saving results...")
    try:
        output_df = pd.DataFrame(output_data)
        output_df.columns = ['Image Name', 'East', 'North', 'Elevation']
        output_file_path = os.path.join(script_directory, 'Camera_coords.txt')
        
        output_df.to_csv(output_file_path, sep=',', index=False, header=False)
        
        print(f"SUCCESS: Results successfully written to: {output_file_path}")
        print(f"         Output contains {len(output_data)} camera positions")
        
        # Show sample of results
        if len(output_data) > 0:
            print("\nSample results:")
            print("Image Name           | East       | North      | Elevation")
            print("-" * 65)
            for i, row in enumerate(output_data[:3]):  # Show first 3 results
                print(f"{row[0][:20]:<20} | {row[1]:10.3f} | {row[2]:10.3f} | {row[3]:9.3f}")
            if len(output_data) > 3:
                print(f"... and {len(output_data) - 3} more entries")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}")
        return False


if __name__ == "__main__":
    try:
        success = camera_position_calculator()
        
        if success:
            print("\n" + "=" * 60)
            print("PROCESSING COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("SUCCESS: Camera position calculation finished")
            print("SUCCESS: Output file created: Camera_coords.txt")
            print("SUCCESS: Ready for use in your drone data analysis")
            print("\nNext steps:")
            print("- Review the output file for accuracy")
            print("- Import coordinates into your GIS software")
            print("- Use coordinates for photogrammetry processing")
        else:
            print("\n" + "=" * 60)
            print("PROCESSING FAILED")
            print("=" * 60)
            print("Please review the error messages above and:")
            print("- Check that all required files are present")
            print("- Verify file formats are correct")
            print("- Ensure image filenames follow expected pattern")
            print("- Try running the script again after fixes")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        print("Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        print("\nPlease report this error if it persists.")
        sys.exit(1)