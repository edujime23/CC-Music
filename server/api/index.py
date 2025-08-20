import os
from aiohttp import web

# --- Define the absolute path to the music directory ---
# This logic remains the same. It finds the 'music' folder
# that Vercel has included in our function's bundle.
BASE_MUSIC_DIR = os.path.abspath(os.path.join(os.getcwd(), 'music'))


# --- Define Request Handlers ---

async def handle_index(request):
    """
    A simple handler to confirm the API is running.
    """
    return web.Response(text="aiohttp API is running. Try /api/list-music")


async def list_music_files(request):
    """
    Recursively finds all files and returns their web-accessible paths.
    """
    all_file_paths = []

    # os.walk is synchronous, which is perfectly fine here as it's fast
    # and runs once per request on the local filesystem.
    for root, dirs, files in os.walk(BASE_MUSIC_DIR):
        for filename in files:
            # Get the path of the file relative to the BASE_MUSIC_DIR
            relative_path = os.path.relpath(os.path.join(root, filename), BASE_MUSIC_DIR)
            
            # Construct the final web path, like /music/foldera/a.lua
            web_path = os.path.join('/music', relative_path)
            
            # Ensure forward slashes for URL compatibility
            web_path = web_path.replace(os.sep, '/')
            
            all_file_paths.append(web_path)

    # Use web.json_response to correctly format the JSON output
    return web.json_response(all_file_paths)


# --- Create and Configure the Application ---

# This 'app' object is what Vercel will serve
app = web.Application()

# Add the routes, linking a path to a handler function
app.router.add_get('/api/index', handle_index)
app.router.add_get('/api/list-music', list_music_files)