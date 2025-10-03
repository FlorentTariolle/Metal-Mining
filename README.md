# DarkLyrics Dataset Scraper and Analyzer

This project, developed for the *Projet d'Approfondissement et d'Ouverture* (PAO) at INSA Rouen, scrapes and analyzes metal music lyrics from [DarkLyrics](http://www.darklyrics.com/) using two Python scripts.

## Team
- **Florent**: Scrapes first quarter of artists.
- **Nizar**: Scrapes second quarter.
- **Mathis**: Scrapes third quarter.
- **Rayen**: Scrapes fourth quarter.

## Features

### 1. Scraper (`scraper.py`)
- Fetches artists, albums, and song lyrics from DarkLyrics.
- Supports multi-user scraping by splitting artists into quarters.
- Saves progress (`progress<quarter>.json`) and outputs user-specific datasets (`complete_dataset_<user>.json`).

### 2. Analyzer (`analyzer.py`)
- Analyzes dataset and visualizes:
  - Songs with/without lyrics (pie chart).
  - Publication types (pie chart).
  - Top 10 bands by song/album count (bar charts).
  - Songs by release year (bar chart).
  - Language distribution (pie chart, top 4 + others; table, top 20).

## Prerequisites
Install required packages:
```bash
pip install -r requirements.txt