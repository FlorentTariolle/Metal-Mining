#!/usr/bin/env python3

"""
Comprehensive script using metalparser to fetch and save the complete dataset from DarkLyrics.
Downloads all artists, their albums, and all songs in each album.
Saves to data/complete_dataset.json
"""

import json
import os
import sys

from metalparser.darklyrics import DarkLyricsApi  # pyright: ignore[reportMissingImports]


def fetch_complete_dataset(api, artists, existing_dataset=None, start_position=0):
	"""
	Fetch complete dataset: artists, their albums, and all songs.
	Returns a nested dictionary structure.
	"""
	complete_dataset = existing_dataset.copy() if existing_dataset else {}
	total_artists = len(artists) + start_position
	
	for i, artist in enumerate(artists, 1):
		absolute_position = start_position + i
		print(f"[{absolute_position}/{total_artists}] Processing artist: {artist}")
		
		try:
			# Get albums for this artist
			albums = api.get_albums_info(artist, title_only=False) or []
			print(f"  Found {len(albums)} albums")
			
			artist_data = {
				"name": artist,
				"albums": {}
			}
			
			for j, album in enumerate(albums, 1):
				# Extract album name from album object if it's a dict
				if isinstance(album, dict):
					album_name = album.get("title", str(album))
				else:
					album_name = str(album)
				
				print(f"    [{j}/{len(albums)}] Processing album: {album_name}")
				
				try:
					# Get songs for this album
					songs_data = api.get_album_info_and_lyrics(album_name, artist, lyrics_only=False) or []
					print(f"      Found {len(songs_data)} songs")
					
					album_data = {
						"name": album_name,
						"songs": []
					}
					
					for song_data in songs_data:
						song_info = {
							"title": song_data.get("title", ""),
							"track_number": song_data.get("track_number", 0),
							"lyrics": song_data.get("lyrics", "")
						}
						album_data["songs"].append(song_info)
					
					artist_data["albums"][album_name] = album_data
										
				except Exception as e:
					print(f"      Error processing album '{album_name}': {e}")
					continue
			
			complete_dataset[artist] = artist_data
			
			# Save progress after each artist (for frequent saves)
			save_progress(complete_dataset, absolute_position, total_artists)
			
		except Exception as e:
			print(f"  Error processing artist '{artist}': {e}")
			continue
	
	return complete_dataset


def save_progress(dataset, current, total):
	"""Save progress to a temporary file."""
	progress_file = os.path.join("data", "progress.json")
	
	# Count total albums and songs for progress info
	total_albums = sum(len(artist_data.get("albums", {})) for artist_data in dataset.values())
	total_songs = sum(
		sum(len(album_data.get("songs", [])) for album_data in artist_data.get("albums", {}).values())
		for artist_data in dataset.values()
	)
	
	progress_data = {
		"dataset": dataset,
		"progress": {
			"current": current,
			"total": total,
			"processed_artists": len(dataset),
			"total_albums": total_albums,
			"total_songs": total_songs
		}
	}
	
	with open(progress_file, "w", encoding="utf-8") as f:
		json.dump(progress_data, f, ensure_ascii=False, indent=2)
	
	print(f"  ✅ Progress saved: {current}/{total} artists ({len(dataset)} completed)")
	print(f"     📊 {total_albums} albums, {total_songs} songs collected so far")


def main():
	out_dir = os.path.abspath("data")
	os.makedirs(out_dir, exist_ok=True)

	# Initialize dataset variable
	dataset = {}

	# Check for existing complete dataset
	dataset_path = os.path.join(out_dir, "complete_dataset.json")
	if os.path.exists(dataset_path):
		print("Complete dataset already exists!")
		with open(dataset_path, "r", encoding="utf-8") as f:
			dataset = json.load(f)
		print(f"Dataset contains {len(dataset)} artists")
		return 0

	# Check for existing progress
	progress_path = os.path.join(out_dir, "progress.json")
	if os.path.exists(progress_path):
		print("Found existing progress file. Loading...")
		try:
			with open(progress_path, "r", encoding="utf-8") as f:
				progress_data = json.load(f)
			dataset = progress_data.get("dataset", {})
			progress_info = progress_data.get("progress", {})
			current = progress_info.get("current", 0)
			total = progress_info.get("total", 0)
			print(f"Resuming from artist {current}/{total}")
			print(f"Already processed {len(dataset)} artists")
			
			# Keep the progress file for now - we'll update it as we go
		except Exception as e:
			print(f"Error loading progress: {e}")
			dataset = {}

	# Check for existing artists list first
	artists_file = os.path.join(out_dir, "artists_list.json")
	if os.path.exists(artists_file):
		print("Loading existing artists list...")
		try:
			with open(artists_file, "r", encoding="utf-8") as f:
				artists = json.load(f) or []
			print(f"Loaded {len(artists)} artists from existing file")
		except (json.JSONDecodeError, IOError) as e:
			print(f"Error loading artists file: {e}")
			artists = []
	else:
		# Initialize API and fetch artists list
		api = DarkLyricsApi(use_cache=False)
		print("Fetching artists list...")
		artists = api.get_artists_list() or []
		print(f"Found {len(artists)} artists")
		
		# Save artists list to avoid losing it
		with open(artists_file, "w", encoding="utf-8") as f:
			json.dump(artists, f, ensure_ascii=False, indent=2)
		print(f"Saved artists list to: {artists_file}")
	
	# Initialize API for dataset fetching
	api = DarkLyricsApi(use_cache=False)

	# If we have existing dataset, filter out already processed artists
	start_position = 0
	if dataset:
		processed_artists = set(dataset.keys())
		remaining_artists = [artist for artist in artists if artist not in processed_artists]
		start_position = len(artists) - len(remaining_artists)
		print(f"Resuming with {len(remaining_artists)} remaining artists (starting from position {start_position + 1})")
		artists = remaining_artists

	if not artists:
		print("No artists to process!")
		return 0

	# Fetch complete dataset
	print("Starting complete dataset fetch...")
	final_dataset = fetch_complete_dataset(api, artists, dataset, start_position)

	# Save complete dataset
	print("Saving complete dataset...")
	with open(dataset_path, "w", encoding="utf-8") as f:
		json.dump(final_dataset, f, ensure_ascii=False, indent=2)
	
	# Clean up progress file if it exists
	if os.path.exists(progress_path):
		os.remove(progress_path)
	
	print(f"Complete dataset saved to: {dataset_path}")
	print(f"Total artists: {len(final_dataset)}")
	
	# Count total albums and songs
	total_albums = sum(len(artist_data.get("albums", {})) for artist_data in final_dataset.values())
	total_songs = sum(
		sum(len(album_data.get("songs", [])) for album_data in artist_data.get("albums", {}).values())
		for artist_data in final_dataset.values()
	)
	
	print(f"Total albums: {total_albums}")
	print(f"Total songs: {total_songs}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
