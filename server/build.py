# server/buid.py
import os
import json

print("--- Generating music file list ---")

# The script runs from the 'server' directory during the Vercel build.
music_source_dir = os.path.abspath('../music')
output_file_path = os.path.abspath('api/music_files.json')

file_paths = []

if not os.path.isdir(music_source_dir):
    print(f"Warning: Source directory '{music_source_dir}' not found. Creating an empty file list.")
else:
    # Recursively walk through the music directory
    for dirpath, _, filenames in os.walk(music_source_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            
            # We get the path relative to the repo root ('..') and add a leading slash
            repo_root = os.path.abspath('..')
            relative_path = os.path.relpath(full_path, repo_root)
            url_path = f"/{relative_path.replace(os.sep, '/')}" # Ensure forward slashes
            
            file_paths.append(url_path)

file_paths.sort()

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

with open(output_file_path, 'w') as f:
    json.dump({'files': file_paths}, f, indent=2)

print(f"Successfully generated file list with {len(file_paths)} entries.")
print(f"Manifest file created at: {output_file_path}")
print("--- Build script finished ---")