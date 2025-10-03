#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_music_data(filepath='data/progress1.json'):
    """Load and process music data from JSON file"""
    
    # Load the JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all songs and their lyrics status
    songs_data = []
    
    for artist_name, artist_info in data['dataset'].items():
        for album_name, album_info in artist_info['albums'].items():
            for song in album_info['songs']:
                has_lyrics = bool(song.get('lyrics', '').strip())
                songs_data.append({
                    'artist': artist_name,
                    'album': album_name,
                    'song': song['title'],
                    'has_lyrics': has_lyrics,
                    'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics'
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
    plt.figure(figsize=(15, 10))
    
    # With vs Without Lyrics
    plt.subplot(2, 2, 1)
    lyrics_counts = df_songs['lyrics_status'].value_counts()
    colors = ['#ff9999', '#66b3ff']
    plt.pie(lyrics_counts.values, labels=lyrics_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Distribution of Songs: With vs Without Lyrics', fontsize=12, fontweight='bold')

    # Publication types pie chart
    plt.subplot(2, 2, 2)
    type_counts = df_albums['album_type'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#cc99ff']
    plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
            colors=colors[:len(type_counts)], startangle=90)
    plt.title('Distribution of Publication Types', fontsize=12, fontweight='bold')

    # Top 10 bands by song count
    plt.subplot(2, 2, 3)
    top_bands = df_songs['artist'].value_counts().head(10)
    plt.barh(top_bands.index[::-1], top_bands.values[::-1])
    plt.title('Top 10 Bands by Song Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Songs')
    plt.ylabel('Bands')
    
    # Top 10 bands by album count
    plt.subplot(2, 2, 4)
    top_bands_albums = df_songs.groupby('artist')['album'].nunique().sort_values(ascending=False).head(10)
    plt.barh(top_bands_albums.index[::-1], top_bands_albums.values[::-1])
    plt.title('Top 10 Bands by Album Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Albums')
    plt.ylabel('Bands')
    
    plt.tight_layout()
    plt.show()
    
    return df_songs, df_albums


if __name__ == "__main__":
    # Load data
    df_songs, df_albums = load_music_data()
    
    # Analyze and visualize
    analyze_lyrics_distribution(df_songs, df_albums)
