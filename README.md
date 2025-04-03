# 🎵 Music League Wrapped

**Music League Wrapped** is a Python-based data storytelling app that transforms raw Music League game data into personalized, meme-filled end-of-season PDF reports for each competitor.

The report includes:
- 🏆 Superlative awards (Most Popular, Best Performance, Least Compatible, etc.)
- 🎯 Personalized voting analytics and track performance breakdowns
- 🎧 Spotify popularity integration via the Spotify Web API
- 📈 Visualizations like podium charts, scatter plots, and tables

## 🚀 Features
- Parses submissions and votes data from Music League
- Aggregates data per round and per competitor
- Calculates custom rankings and superlatives
- Visualizes insights with charts and custom meme images
- Exports full multi-page PDF reports for all competitors

## 🔧 Built With
- Python
- Pandas
- Matplotlib
- ReportLab
- Spotipy (Spotify API wrapper)

## 📂 Input Files
- `input_data/`: Music League CSV exports
- `.env`: For Spotify API credentials

## 📤 Output
- `output/`: Auto-generated PDF reports and visual assets

## 🧠 Use Case
A fun way to celebrate and reflect on your Music League season with data-driven insights, humor, and personalized trophies.

---
## 📄 Sample Report

Download a full example report from the project:

👉 [Download sample_report.zip](https://github.com/mattlally/MusicLeagueWrapped/raw/main/sample_report.zip)

---
## ⚙️ How to Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/mattlally/MusicLeagueWrapped.git
cd MusicLeagueWrapped

### 2. Set up your environment
python3 -m venv venv
source venv/bin/activate  # or `source venv/bin/activate.fish` / `venv\Scripts\activate` on Windows
pip install -r requirements.txt

### 3. Add your Spotify credentials (create a .env file at the root with:)
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

### 4. Add your Music League CSVs (drop your .csv exports into the input_data/ folder)

### 5. Run it!
python main.py

PDF report will be saved in the output/ folder.

