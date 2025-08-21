import os
import json

def get_files_recursively(directory, base_dir):
    """Recursively get all files in a directory"""
    files = []
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, base_dir)
            # Convert Windows paths to Unix-style
            relative_path = relative_path.replace('\\', '/')
            
            files.append({
                "path": relative_path,
                "name": filename,
                "size": os.path.getsize(file_path)
            })
    
    return files

# Get the music directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up from server/scripts to find music folder
music_dir = os.path.join(script_dir, '..', '..', 'music')
music_dir = os.path.abspath(music_dir)

print(f"Looking for music directory at: {music_dir}")

if not os.path.exists(music_dir):
    print(f"ERROR: Music directory not found at {music_dir}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    # Create empty file list if music dir doesn't exist
    files = []
else:
    # Generate file list
    files = get_files_recursively(music_dir, music_dir)
    print(f"Found {len(files)} files")

# Save to JSON - IMPORTANT: Save in server/data, not server/scripts/data
output_dir = os.path.join(script_dir, '..', 'data')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'music-files.json')
with open(output_path, 'w') as f:
    json.dump(files, f, indent=2)

print(f"Generated file list at: {output_path}")
print(f"File exists: {os.path.exists(output_path)}")