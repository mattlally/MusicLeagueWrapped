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
```

### 2. Set up your environment
```bash
python3 -m venv venv
source venv/bin/activate  # or `source venv/bin/activate.fish` / `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 3. Add your Spotify credentials (create a .env file at the root with:)
```env
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

### 4. Add your Music League CSVs
Drop your .csv exports into the input_data/ folder. You will need to create the input_data/ folder if it doesn't exist.

### 5. Add your memes (optional)
Drop your meme images into the meme_pics/ folder. You will need to create the meme_pics/ folder if it doesn't exist. Use the following naming convention for the images:


| Meme Category                     | Image Name           |
| --------------------------------- | -------------------- |
| Most Popular                      | winner.png           |
| Most Likely to Lose Soo Badly Oof | loser.png            |
| Most Likely to Be Average as Hell | avg.png              |
| Best Performance                  | performance.png      |
| Chatty Cathy                      | chatty.png           |
| The Author                        | author.png           |
| Crowd Pleaser                     | crowd_pleasers.png   |
| Trend Setter                      | trendy.png           |
| Most Compatible                   | most_compatible.png  |
| Least Compatible                  | least_compatible.png |
| Most Similar                      | most_similar.png     |
| Least Similar                     | least_similar.png    |
| Most Likely to Vote First         | early_vote.png       |
| Most Likely to Vote Last          | late_vote.png        |


### 6. Run it!
```bash
python main.py
```

### 7. Check out your report!

PDF report will be saved in the output/ folder.

