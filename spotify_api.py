import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

def get_client_credentials_token():
    """Fetch an access token using the Client Credentials Flow."""
    token_response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    token_response.raise_for_status()
    token_data = token_response.json()
    return token_data["access_token"]

def get_track_popularity(track_id, token):
    """Fetch and return only the popularity of a given track."""
    track_id = track_id.split(":")[-1]  # Ensure correct format
    url = f"{SPOTIFY_API_BASE_URL}/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    #print(f"🔍 Requesting Track Popularity: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    track_data = response.json()
    popularity = track_data.get("popularity", None)  # Extract popularity

    #print(f"🎧 Popularity: {popularity}")
    return popularity

# ✅ Test Spotify API (Optional)
if __name__ == "__main__":
    token = get_client_credentials_token()
    print("🔑 Acquired Client Credentials Token:", token)

    test_track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Example track ID

    # Get and print track popularity
    track_popularity = get_track_popularity(test_track_id, token)
    print(f"\n🎵 Track Popularity: {track_popularity}")
