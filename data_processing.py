import pandas as pd
import requests


def load_csv_data(base_path):
    """Loads CSV data into pandas DataFrames."""
    competitors = pd.read_csv(f"{base_path}/input_data/competitors.csv")
    rounds = pd.read_csv(f"{base_path}/input_data/rounds.csv")
    submissions = pd.read_csv(f"{base_path}/input_data/submissions.csv")
    votes = pd.read_csv(f"{base_path}/input_data/votes.csv")
    return competitors, rounds, submissions, votes


def most_votes_cast(votes, submissions):
    """Determine the highest number of votes each competitor casted for a single song and the song title."""
    max_votes = votes.loc[
        votes.groupby('Voter ID')['Points Assigned'].idxmax(), ['Voter ID', 'Spotify URI', 'Points Assigned']
    ]
    max_votes = max_votes.merge(submissions[['Spotify URI', 'Title']], on='Spotify URI', how='left')

    return {
        row['Voter ID']: {
            'Votes': row['Points Assigned'],
            'Song': row['Title'],
            'Spotify URI': row['Spotify URI']  # ✅ Now we return the URI!
        }
        for _, row in max_votes.iterrows()
    }



def biggest_fan(votes, submissions):
    """Determine the competitor who voted the most for each submitter."""
    votes_with_submitter = votes.merge(submissions[['Spotify URI', 'Submitter ID']], on='Spotify URI')
    biggest_fans = votes_with_submitter.groupby(['Submitter ID', 'Voter ID'])['Points Assigned'].sum()
    return biggest_fans.groupby(level=0).idxmax().to_dict()


def highest_scoring_submission(votes, submissions):
    """Determine the highest scoring submission for each competitor."""
    song_scores = votes.groupby('Spotify URI')['Points Assigned'].sum()
    submissions['Total Votes'] = submissions['Spotify URI'].map(song_scores)
    top_submissions = submissions.nlargest(3, 'Total Votes')
    return top_submissions[['Submitter ID', 'Title', 'Total Votes']].to_dict('records')


def competitor_comments(votes, submissions):
    """Store all comments a competitor left along with the song they commented on."""
    votes_with_songs = votes.merge(submissions[['Spotify URI', 'Title']], on='Spotify URI', how='left')

    # Ensure all missing comments are replaced with empty strings
    votes_with_songs['Comment'] = votes_with_songs['Comment'].fillna("")

    comments_data = votes_with_songs.groupby('Voter ID').apply(
        lambda x: {
            'Total Comments': len(x),
            'Longest Comment': max(x['Comment'], key=len) if len(x) > 0 else ''
        }).to_dict()

    return comments_data


def competitor_song_performance(submissions, votes):
    """Store all songs each competitor submitted along with total votes received for each song."""
    song_votes = votes.groupby('Spotify URI')['Points Assigned'].sum()
    submissions['Total Votes'] = submissions['Spotify URI'].map(song_votes)
    performance_data = submissions.groupby('Submitter ID').apply(
        lambda x: x[['Title', 'Total Votes']].to_dict('records')).to_dict()
    return performance_data


def get_top_songs_by_votes(submissions, votes, top_n=3):
    """Fetches the top N unique songs based on total votes received for each unique submission (URI + Round)."""
    # Group votes by Spotify URI and Round ID, summing the total votes
    grouped_votes = (
        votes.groupby(['Spotify URI', 'Round ID'])['Points Assigned']
        .sum()
        .reset_index()
    )

    # Merge with submissions to get song details (Title, Artist, Submitter ID)
    merged_df = grouped_votes.merge(
        submissions[['Spotify URI', 'Title', 'Artist(s)', 'Submitter ID', 'Round ID']],
        on=['Spotify URI', 'Round ID'],
        how='left'
    )

    # Sort by Points Assigned in descending order and get the top N unique submissions
    top_songs = merged_df.sort_values(by='Points Assigned', ascending=False).head(top_n)

    # Return relevant columns as a list of dictionaries
    return top_songs[['Title', 'Submitter ID', 'Points Assigned', 'Artist(s)']].to_dict('records')




def calculate_compatibility_scores(votes, competitors, submissions):
    """Calculate compatibility scores based on mutual voting percentages."""

    votes_with_submitter = votes.merge(submissions[['Spotify URI', 'Submitter ID']], on='Spotify URI')
    vote_given = votes_with_submitter.groupby(['Voter ID', 'Submitter ID'])['Points Assigned'].sum()

    #print(f"Votes Given by Each Competitor:\n{vote_given}\n")  # Debugging Info

    compatibility_scores = {}

    for voter in competitors['ID']:
        voter_scores = {}
        for other in competitors['ID']:
            if voter != other:
                given = vote_given.loc[voter, other] if (voter, other) in vote_given.index else 0
                other_given = vote_given.loc[other, voter] if (other, voter) in vote_given.index else 0

                total_given = votes.groupby('Voter ID')['Points Assigned'].sum().get(voter, 1)
                total_given_other = votes.groupby('Voter ID')['Points Assigned'].sum().get(other, 1)

                percent_given = (given / total_given) * 100 if total_given else 0
                percent_other_given = (other_given / total_given_other) * 100 if total_given_other else 0
                compatibility_score = (percent_given + percent_other_given) / 2

                # 🛠 FIX: Return a dictionary instead of a single number
                voter_scores[competitors.loc[competitors['ID'] == other, 'Name'].values[0]] = {
                    "percent_given": round(percent_given, 2),
                    "percent_other_given": round(percent_other_given, 2),
                    "compatibility_score": round(compatibility_score, 2)
                }

                # Debugging info
                # print(
                #     f"{competitors.loc[competitors['ID'] == voter, 'Name'].values[0]} → {competitors.loc[competitors['ID'] == other, 'Name'].values[0]}:")
                # print(f"    Given: {given}, Total Given: {total_given}, Percent Given: {percent_given:.2f}%")
                # print(
                #     f"    Other Given: {other_given}, Total Given Other: {total_given_other}, Percent Other Given: {percent_other_given:.2f}%")
                # print(f"    Compatibility Score: {compatibility_score:.2f}%\n")

        compatibility_scores[competitors.loc[competitors['ID'] == voter, 'Name'].values[0]] = voter_scores

    return compatibility_scores


def get_track_popularity(track_id, token):
    """Fetch and return only the popularity of a given track."""
    track_id = track_id.split(":")[-1]  # Ensure correct format
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"🔍 Requesting Track Popularity: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    track_popularity = response.json()
    popularity = track_popularity.get("popularity", None)  # Extract popularity

    print(f"🎧 Popularity: {popularity}")
    return popularity
