# server/build.py
import os
import json

print("--- Generating music file list with URLs ---")

# --- Your Repository Details ---
REPO_OWNER = 'edujime23'
REPO_NAME = 'CC-Music'
REPO_BRANCH = 'dev' # Or 'main', whichever branch has the music

# --- Script Logic ---
music_source_dir = os.path.abspath('../music')
output_file_path = os.path.abspath('api/music_files.json')

file_data = []

if not os.path.isdir(music_source_dir):
    print(f"Warning: Source directory '{music_source_dir}' not found.")
else:
    for dirpath, _, filenames in os.walk(music_source_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            
            repo_root = os.path.abspath('..')
            relative_path = os.path.relpath(full_path, repo_root).replace(os.sep, '/')
            
            # Construct the direct URL to the raw file content
            raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{relative_path}"
            
            file_data.append({
                "path": f"/{relative_path}", # e.g., /music/a/b/song.mp3
                "raw_url": raw_url
            })

# Sort the list alphabetically by path
file_data.sort(key=lambda x: x['path'])

# Ensure the target directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Write the rich data to the JSON file
with open(output_file_path, 'w') as f:
    json.dump({'files': file_data}, f, indent=2)

print(f"Successfully generated file manifest with {len(file_data)} entries.")
print("--- Build script finished ---")