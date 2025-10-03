#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from langdetect import detect, DetectorFactory

# Ensure consistent language detection results
DetectorFactory.seed = 0

def load_music_data(filepath='data/progress1.json'):
    """Load and process music data from JSON file"""
    
    # Load the JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all songs and their lyrics status
    songs_data = []
    
    for artist_name, artist_info in data['dataset'].items():
        for album_name, album_info in artist_info['albums'].items():
            release_year = album_info.get('release_year', 'Unknown')
            for song in album_info['songs']:
                lyrics = song.get('lyrics', '').strip()
                has_lyrics = bool(lyrics)
                language = detect(lyrics) if has_lyrics else 'None'
                songs_data.append({
                    'artist': artist_name,
                    'album': album_name,
                    'song': song['title'],
                    'release_year': release_year,
                    'has_lyrics': has_lyrics,
                    'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics',
                    'language': language
                })
    
    # Create DataFrame for songs
    df_songs = pd.DataFrame(songs_data)
    
    # Extract album types
    album_types = []
    
    for artist_name, artist_info in data['dataset'].items():
        for album_name, album_info in artist_info['albums'].items():
            album_type = album_info.get('album_type', 'Unknown')
            album_types.append(album_type)
    
    # Create DataFrame for album types
    df_albums = pd.DataFrame({'album_type': album_types})
    
    return df_songs, df_albums


def analyze_lyrics_distribution(df_songs, df_albums):
    """Analyze and visualize the distribution of music with and without lyrics"""
    
    # Create visualization
    plt.figure(figsize=(18, 12))
    
    # With vs Without Lyrics
    plt.subplot(3, 2, 1)
    lyrics_counts = df_songs['lyrics_status'].value_counts()
    colors = ['#ff9999', '#66b3ff']
    total = lyrics_counts.sum()
    percentages = [(status, f"{status} ({(count/total*100):.1f}%)") for status, count in lyrics_counts.items()]
    labels = [label for _, label in percentages]
    plt.pie(lyrics_counts.values, colors=colors, startangle=90)
    plt.legend(labels, title="Lyrics Status", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Songs: With vs Without Lyrics', fontsize=12, fontweight='bold')

    # Publication types pie chart
    plt.subplot(3, 2, 2)
    type_counts = df_albums['album_type'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#cc99ff']
    total = type_counts.sum()
    percentages = [(type_, f"{type_} ({(count/total*100):.1f}%)") for type_, count in type_counts.items()]
    labels = [label for _, label in percentages]
    plt.pie(type_counts.values, colors=colors[:len(type_counts)], startangle=90)
    plt.legend(labels, title="Publication Types", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Publication Types', fontsize=12, fontweight='bold')

    # Top 10 bands by song count
    plt.subplot(3, 2, 3)
    top_bands = df_songs['artist'].value_counts().head(10)
    plt.barh(top_bands.index[::-1], top_bands.values[::-1])
    plt.title('Top 10 Bands by Song Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Songs')
    plt.ylabel('Bands')
    
    # Top 10 bands by album count
    plt.subplot(3, 2, 4)
    top_bands_albums = df_songs.groupby('artist')['album'].nunique().sort_values(ascending=False).head(10)
    plt.barh(top_bands_albums.index[::-1], top_bands_albums.values[::-1])
    plt.title('Top 10 Bands by Album Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Albums')
    plt.ylabel('Bands')

    # Distribution of songs over the years
    plt.subplot(3, 2, 5)
    # Filter out 'Unknown' years and convert to numeric
    year_data = df_songs[df_songs['release_year'] != 'Unknown'].copy()
    year_data['release_year'] = pd.to_numeric(year_data['release_year'], errors='coerce')
    year_data = year_data.dropna(subset=['release_year'])
    
    # Count songs per year
    year_counts = year_data['release_year'].value_counts().sort_index()
    
    plt.bar(year_counts.index, year_counts.values)
    plt.title('Distribution of Songs Over the Years', fontsize=12, fontweight='bold')
    plt.xlabel('Release Year')
    plt.ylabel('Number of Songs')
    
    # Set x-axis to show all years
    plt.xticks(year_counts.index, rotation=45)

    # Language distribution for songs with lyrics (Top 4 + Other)
    plt.subplot(3, 2, 6)
    language_counts = df_songs[df_songs['has_lyrics']]['language'].value_counts()
    top_languages = language_counts.head(4)
    other_count = language_counts[4:].sum() if len(language_counts) > 4 else 0
    if other_count > 0:
        top_languages['Other Languages'] = other_count
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#cc99ff']
    # Calculate percentages for legend
    total = top_languages.sum()
    percentages = [(lang, f"{lang} ({(count/total*100):.1f}%)") for lang, count in top_languages.items()]
    labels = [label for _, label in percentages]
    plt.pie(top_languages.values, colors=colors[:len(top_languages)], startangle=90)
    plt.legend(labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Song Languages (Top 4 + Other)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    return df_songs, df_albums


if __name__ == "__main__":
    # Load data
    df_songs, df_albums = load_music_data()
    
    # Analyze and visualize
    analyze_lyrics_distribution(df_songs, df_albums)
