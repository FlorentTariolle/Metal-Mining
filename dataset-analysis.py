#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_lyrics_distribution():
    """Analyze and visualize the distribution of music with and without lyrics"""
    
    # Load the JSON data
    with open('data/progress1.json', 'r', encoding='utf-8') as f:
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
    
    # Create DataFrame
    df = pd.DataFrame(songs_data)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # With vs Without Lyrics
    plt.subplot(2, 2, 1)
    lyrics_counts = df['lyrics_status'].value_counts()
    colors = ['#ff9999', '#66b3ff']
    plt.pie(lyrics_counts.values, labels=lyrics_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Distribution of Songs: With vs Without Lyrics', fontsize=14, fontweight='bold')

    # Top 10 bands by song count
    plt.subplot(2, 2, 2)
    top_bands = df['artist'].value_counts().head(10)
    plt.barh(top_bands.index[::-1], top_bands.values[::-1])
    plt.title('Top 10 Bands by Song Count')
    plt.xlabel('Number of Songs')
    plt.ylabel('Bands')
    
    # Top 10 bands by album count
    plt.subplot(2, 2, 3)
    top_bands_albums = df.groupby('artist')['album'].nunique().sort_values(ascending=False).head(10)
    plt.barh(top_bands_albums.index[::-1], top_bands_albums.values[::-1])
    plt.title('Top 10 Bands by Album Count')
    plt.xlabel('Number of Albums')
    plt.ylabel('Bands')
    
    plt.tight_layout()
    plt.show()
    
    return df

if __name__ == "__main__":
    df = analyze_lyrics_distribution()
