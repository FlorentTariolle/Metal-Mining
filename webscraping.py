#!/usr/bin/env python3

"""
Minimal script using metalparser to fetch and save the full artists list from DarkLyrics.
Saves to data/artists.json
"""

import json
import os
import sys

from metalparser.darklyrics import DarkLyricsApi


def main() -> int:
	out_dir = os.path.abspath("data")
	os.makedirs(out_dir, exist_ok=True)

	# Disable cache to avoid possible requests-cache/SQLiteCache compatibility issues
	api = DarkLyricsApi(use_cache=False)

	artists = api.get_artists_list() or []
	print(f"Found {len(artists)} artists")

	artists_cache_path = os.path.join(out_dir, "artists.json")
	with open(artists_cache_path, "w", encoding="utf-8") as f:
		json.dump(artists, f, ensure_ascii=False, indent=2)
	print(f"Saved artists to: {artists_cache_path}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
