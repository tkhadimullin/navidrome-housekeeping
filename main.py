import os
import time
import shutil
import asyncio
from pathlib import Path
from navidrome_client import NavidromeClient

NAVIDROME_URL = os.getenv("NAVIDROME_URL").rstrip("/")
NAVIDROME_USERNAME = os.getenv("NAVIDROME_USERNAME")
NAVIDROME_PASSWORD = os.getenv("NAVIDROME_PASSWORD")
TARGET_DIR = Path(os.getenv("TARGET_DIR", "/deleted_songs"))
LIBRARY_DIR = Path(os.getenv("LIBRARY_DIR", "/music"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
TARGET_RATING = int(os.getenv("TARGET_RATING", "1"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes", "on")

TARGET_DIR.mkdir(parents=True, exist_ok=True)

navidrome_client = NavidromeClient(NAVIDROME_URL, NAVIDROME_USERNAME, NAVIDROME_PASSWORD)


async def get_starred_tracks():
    """Return all tracks that are starred (have a rating)."""
    resp = await navidrome_client.api_call("/api/song")    
    return resp or []

def move_preserving_structure(relative_path: Path):
    """Move a file, recreating its relative directory structure under TARGET_DIR."""
    
    absolute_src_path = Path(LIBRARY_DIR, relative_path)
    if not absolute_src_path.exists():
        print(f"File not found on disk: {absolute_src_path}")
        return    

    dest_path = Path(TARGET_DIR, relative_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Moving {absolute_src_path} → {dest_path}")
    if not DRY_RUN: shutil.move(str(absolute_src_path), dest_path)

async def main():
    print(f"Monitoring for songs with rating == {TARGET_RATING} every {POLL_INTERVAL}s...")

    while True:
        try:
            tracks = await get_starred_tracks()
            one_star_tracks = [t for t in tracks if int(t.get("rating", 0)) == TARGET_RATING]

            if not one_star_tracks:
                print("No 1-star tracks found. Waiting...")
            else:
                print(f"Found {len(one_star_tracks)} tracks with rating {TARGET_RATING} to move...")

            for track in one_star_tracks:
                src_path = track.get("path")
                if not src_path:
                    print(f"Could not determine file path for {track.get('title', 'unknown')}")
                    continue

                move_preserving_structure(src_path)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())