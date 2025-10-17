#!/usr/bin/env python3

import json
import tqdm
import os
from langdetect import detect, DetectorFactory
from langdetect import LangDetectException
from wordcloud import WordCloud
from analyzer import LANGUAGE_MAP
import argparse

import nltk

nltk.download('punkt', quiet=True)
try:
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist, word_tokenize
import string
import pandas as pd
import matplotlib.pyplot as plt

csv_cache_path = "cache/lyrics_data.csv"


def load_music_data_with_lyrics(filepath='data/progress2.json'):
    """
    Load and process music data from a JSON file, including lyrics and language detection.

    Args:
        filepath (str): Path to the JSON data file.

    Returns:
        pd.DataFrame: Processed DataFrame containing song metadata and lyrics.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    songs_data = []

    total_songs = sum(
        len(album_info.get('songs', []))
        for artist_info in data.get('dataset', {}).values()
        for album_info in artist_info.get('albums', {}).values()
    )

    from tqdm import tqdm
    with tqdm(total=total_songs, desc='Loading songs', unit='song') as pbar:
        for artist_name, artist_info in data.get('dataset', {}).items():
            for album_name, album_info in artist_info.get('albums', {}).items():
                release_year = album_info.get('release_year', 'Unknown')
                for song in album_info.get('songs', []):
                    lyrics = song.get('lyrics', '').strip()
                    has_lyrics = bool(lyrics) and len(lyrics) >= 5
                    if has_lyrics:
                        try:
                            language = detect(lyrics)
                        except LangDetectException:
                            language = 'None'
                    else:
                        language = 'None'
                    language = LANGUAGE_MAP.get(language, language) if language != 'None' else 'None'
                    songs_data.append({
                        'artist': artist_name,
                        'album': album_name,
                        'song': song.get('title', ''),
                        'release_year': release_year,
                        'has_lyrics': has_lyrics,
                        'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics',
                        'language': language,
                        'lyrics': lyrics
                    })
                    pbar.update(1)

    df_songs = pd.DataFrame(songs_data)
    return df_songs


STOPWORDS = list(set([str(line.rstrip('\n')) for line in open("resources/stopwords_eng.txt", "r")]))
PUNCTUATION = list(string.punctuation) + ['..', '...', '’', "''", '``', '`']

def drop_songs_with_no_lyrics(dataframe):
    """
    Drop all songs without lyrics from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only songs that have lyrics.
    """
    initial_count = len(dataframe)
    dataframe = dataframe[dataframe['has_lyrics']]
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs without lyrics.")
    return dataframe


def drop_songs_that_are_not_english(dataframe):
    """
    Drop all songs that are not in English from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only English-language songs.
    """
    initial_count = len(dataframe)
    dataframe = dataframe[dataframe['language'] == 'English']
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs that are not in English.")
    return dataframe


def get_word_frequence_distribution(df, text_column='lyrics'):
    """
    Compute word frequency distribution from a text column in the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the text data.
        text_column (str): Column name containing the text (lyrics).

    Returns:
        FreqDist: NLTK frequency distribution of words.
    """
    words_corpus = " ".join(df[text_column].dropna().astype(str).values)
    words_corpus = words_corpus.lower().replace('\\n', ' ')
    try:
        tokens = nltk.word_tokenize(words_corpus)
    except LookupError:
        nltk.download('punkt', quiet=True)
        try:
            tokens = nltk.word_tokenize(words_corpus)
        except LookupError:
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(words_corpus)

    word_freq_dist = FreqDist(tokens)

    # remove punctuation and stopwords
    for stopword in STOPWORDS:
        if stopword in word_freq_dist:
            del word_freq_dist[stopword]

    for punctuation in PUNCTUATION:
        if punctuation in word_freq_dist:
            del word_freq_dist[punctuation]

    return word_freq_dist


def plot_word_cloud(freq, output_path=None):
    """
    Generate and either save the image or not depending on output_path.

    Args:
        freq (FreqDist): Word frequency distribution.
        output_path (str, optional): Path to save the word cloud image.
                                     If None, the image will not be saved.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate_from_frequencies(freq)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Lyrics', fontsize=20)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
        print(f"Word cloud saved to {output_path}")


def plot_word_cloud_Debauchery(dataframe):
    """
    Generate and display a word cloud for Linkin Park lyrics.
    """
    Debauchery_songs = dataframe[dataframe['artist'] == 'Debauchery']
    Debauchery_word_freq_dist = get_word_frequence_distribution(Debauchery_songs, text_column='lyrics')
    plot_word_cloud(Debauchery_word_freq_dist)
    print(Debauchery_word_freq_dist.most_common(20))
    plt.savefig("output_pics/Debauchery_wordcloud.png", bbox_inches='tight')

if __name__ == "__main__":
    """
    Main execution flow:
    - Parses arguments for input JSON and optional output image path.
    - Loads and filters song lyrics data.
    - Computes word frequencies.
    - Plots or saves the word cloud.
    - Prints the top 20 most common words.
    """
    parser = argparse.ArgumentParser(description="Analyze lyrics data from a JSON file.")
    parser.add_argument("-f", "--filepath", default="data/progress2.json",
                        help="Path to json file (ex: `data/progress2.json`).")
    parser.add_argument("-o", "--output", default=None,
                        help="Path to output image. If not provided, image won't be saved.")
    args = parser.parse_args()

    if os.path.exists(csv_cache_path):
        print(f"Loading cached data from {csv_cache_path}...")
        df_songs = pd.read_csv(csv_cache_path)
    else:
        print("CSV cache not found. Loading from JSON and creating cache...")
        df_songs = load_music_data_with_lyrics(args.filepath)
        os.makedirs("cache", exist_ok=True)
        df_songs.to_csv(csv_cache_path, index=False)
        print(f"Data cached to {csv_cache_path}")

    df_songs = drop_songs_with_no_lyrics(df_songs)
    df_songs_english = drop_songs_that_are_not_english(df_songs)
    metal_word_freq_dist = get_word_frequence_distribution(df_songs, text_column='lyrics')
    plot_word_cloud(metal_word_freq_dist, args.output)
    plot_word_cloud_Debauchery(df_songs_english)
    print(metal_word_freq_dist.most_common(20))

