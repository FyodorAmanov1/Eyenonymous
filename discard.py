"""
Discard/Clean up utility - Removes all image files from the directory
while preserving the main opencv.py file and this script.
"""

import os
import glob


def discard_images():
    """
    Delete all image files in the current directory.
    Keeps only .py files (opencv.py and discard.py).
    """
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Image file extensions to delete
    image_extensions = [
        '*.jpg', '*.jpeg', '*.png', '*.bmp', 
        '*.gif', '*.tiff', '*.webp', '*.JPG', 
        '*.JPEG', '*.PNG'
    ]
    
    deleted_count = 0
    deleted_files = []
    
    print("=" * 60)
    print("Image Cleanup Utility")
    print("=" * 60)
    print(f"Scanning directory: {current_dir}")
    print()
    
    # Find and delete all image files
    for extension in image_extensions:
        pattern = os.path.join(current_dir, extension)
        files = glob.glob(pattern)
        
        for file_path in files:
            try:
                file_name = os.path.basename(file_path)
                os.remove(file_path)
                deleted_files.append(file_name)
                deleted_count += 1
                print(f"✓ Deleted: {file_name}")
            except Exception as e:
                print(f"✗ Failed to delete {file_name}: {e}")
    
    print()
    print("=" * 60)
    
    if deleted_count > 0:
        print(f"✓ Cleanup complete!")
        print(f"✓ Total files deleted: {deleted_count}")
        print()
        print("Deleted files:")
        for file_name in deleted_files:
            print(f"  - {file_name}")
    else:
        print("ℹ No image files found to delete")
    
    print("=" * 60)
    print("✓ opencv.py preserved")
    print("✓ discard.py preserved")
    print("=" * 60)


def discard_with_confirmation():
    """
    Delete images with user confirmation.
    """
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Image file extensions to check
    image_extensions = [
        '*.jpg', '*.jpeg', '*.png', '*.bmp', 
        '*.gif', '*.tiff', '*.webp', '*.JPG', 
        '*.JPEG', '*.PNG'
    ]
    
    # Count images
    image_files = []
    for extension in image_extensions:
        pattern = os.path.join(current_dir, extension)
        image_files.extend(glob.glob(pattern))
    
    if not image_files:
        print("ℹ No image files found to delete")
        return
    
    print("=" * 60)
    print("Image Cleanup Utility - Confirmation Mode")
    print("=" * 60)
    print(f"Found {len(image_files)} image file(s):")
    print()
    
    for file_path in image_files:
        print(f"  - {os.path.basename(file_path)}")
    
    print()
    response = input(f"Delete all {len(image_files)} image file(s)? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        discard_images()
    else:
        print("\n✗ Cleanup cancelled")
        print("=" * 60)


def main():
    """
    Main function - runs cleanup with confirmation.
    """
    import sys
    
    # Check if --force flag is provided
    if '--force' in sys.argv or '-f' in sys.argv:
        print("Running in FORCE mode (no confirmation)...")
        print()
        discard_images()
    else:
        discard_with_confirmation()


if __name__ == "__main__":
    main()
