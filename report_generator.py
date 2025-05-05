import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from data_processing import (
    load_csv_data, most_votes_cast, biggest_fan, highest_scoring_submission,
    competitor_comments, competitor_song_performance, calculate_compatibility_scores,
    get_top_songs_by_votes, get_track_popularity
)
from visuals import create_podium_visual, plot_popularity_chart
from spotify_api import get_client_credentials_token

# Constants
report_title = "Music League"
report_subtitle = "Wrapped Analysis"


def generate_pdf(base_path):
    """Generates the full Music League report PDF."""
    output_dir = os.path.join(base_path, 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, 'music_league_report.pdf')
    doc = []

    # Formatting
    custom_font = "Helvetica-Bold"  # Fallback

    styles = getSampleStyleSheet()

    styles["Title"].fontName = custom_font  # Use Circular-Black or fallback
    styles["Title"].textColor = "#1DB954"  # Spotify Green
    styles["Title"].fontSize = 36  # Large Title

    styles["Heading1"].fontName = custom_font
    styles["Heading1"].textColor = "#000000"
    styles["Heading1"].fontSize = 24  # Adjust size

    styles["Heading2"].fontName = custom_font
    styles["Heading2"].textColor = "#1DB954"
    styles["Heading2"].fontSize = 18  # Adjust size

    styles["Normal"].fontName = custom_font  # Use for body text
    styles["Normal"].fontSize = 12  # Standard text size

    # 🎨 Define styles for headings and content
    summary_heading_style = ParagraphStyle(
        'SummaryHeading',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.blue,
        spaceAfter=6
    )

    summary_content_style = ParagraphStyle(
        'SummaryContent',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.black,
        spaceAfter=4
    )

    icon_style = ParagraphStyle(
        'IconStyle',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.darkred
    )

    # Define mapping of superlatives to image filenames
    meme_pics_dir = os.path.join(base_path, "meme_pics")
    meme_images = {
        "Most Popular": "winner.png",
        "Most Likely to Lose Soo Badly Oof": "loser.png",
        "Most Likely to Be Average as Hell": "avg.png",
        "Best Performance": "performance.png",
        "Chatty Cathy": "chatty.png",
        "The Author": "author.png",
        "Crowd Pleaser": "crowd_pleasers.png",
        "Trend Setter": "trendy.png",
        "Most Compatible": "most_compatible.png",
        "Least Compatible": "least_compatible.png",
        "Most Similar": "most_similar.png",
        "Least Similar": "least_similar.png",
        "Most Likely to Vote First": "early_vote.png",
        "Most Likely to Vote Last": "late_vote.png"
    }

    def add_meme_image(superlative_name):
        """Adds a corresponding meme image for a superlative if available."""
        image_filename = meme_images.get(superlative_name)
        if image_filename:
            image_path = os.path.join(meme_pics_dir, image_filename)
            if os.path.exists(image_path):
                doc.append(Image(image_path, width=200, height=150))  # Adjust as needed

    competitors, rounds, submissions, votes = load_csv_data(base_path)
    token = get_client_credentials_token()

    # Place this at the beginning of `generate_pdf`, right after you load competitors.
    superlative_wins = {competitor_id: [] for competitor_id in competitors['ID']}

    # Helper function to add ordinal suffix to a number (1 -> 1st, 2 -> 2nd, etc.)
    def ordinal_suffix(n):
        """Returns a string with the ordinal suffix for a given integer."""
        if 11 <= n % 100 <= 13:
            return f"{n}th"
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    # Add Cover Page with color styling
    doc.append(Paragraph(
        f"<font color='black'>{report_title}</font><br/><br/><font color='#1DB954'>{report_subtitle}</font>",
        styles['Title']
    ))
    doc.append(Spacer(1, 50))  # Add space before image

    # Path to the cover image
    cover_image_path = os.path.join(base_path, "meme_pics", "vibe_investigation.png")

    # Check if the image exists before adding it
    if os.path.exists(cover_image_path):
        doc.append(Image(cover_image_path, width=400, height=300))

    # Add a page break to move to the next section
    doc.append(PageBreak())

    # Title
    doc.append(Paragraph("What is this Document?", styles['Heading1']))
    doc.append(Spacer(1, 12))  # Add spacing after the title for better readability

    # Intro Paragraph
    intro_text = """
    This document provides a comprehensive overview of your participation in the Music League, highlighting your statistics, achievements, and insights from the season. Think of it as your personal “Wrapped” experience for the Music League!
    """
    doc.append(Paragraph(intro_text, styles['BodyText']))
    doc.append(Spacer(1, 20))  # Add more space before the "Sections" heading

    # Sections Overview
    doc.append(Paragraph("Sections", styles['Heading2']))

    # Superlatives Section
    doc.append(Paragraph("Superlatives", styles['Heading3']))
    superlative_bullets = [
        "<b>Most Popular:</b> The competitors with the most total votes.",
        "<b>Most Likely to Lose Soo Badly Oof:</b> The competitors with the fewest total votes lmao.",
        "<b>Most Likely to Be Average as Hell:</b> The competitors who placed dead center.",
        "<b>Best Performance:</b> The top 3 individual songs with the highest votes.",
        "<b>Chatty Cathy:</b> The competitors who left the most comments while voting.",
        "<b>The Author:</b> The competitors who wrote the longest comments while voting.",
        "<b>Crowd Pleaser:</b> Competitors whose songs had the highest average Spotify popularity.",
        "<b>Trend Setters:</b> The competitors whose songs had the lowest average Spotify popularity.",
        "<b>Most Compatible:</b> Pairs of competitors who voted most for one another.",
        "<b>Least Compatible:</b> Pairs of competitors who voted least for one another.",
        "<b>Most Similar:</b> Pairs of competitors with the most similar voting patterns.",
        "<b>Least Similar:</b> Pairs of competitors with the least similar voting patterns.",
        "<b>Most Likely to Vote First:</b> Competitors who submitted their votes earliest on average.",
        "<b>Most Likely to Vote Last:</b> Competitors who submitted their votes latest on average."
    ]

    for bullet in superlative_bullets:
        doc.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;➤ {bullet}", styles['BodyText']))

    doc.append(Spacer(1, 24))  # Add space before the next section

    # Individual Wrapped Analysis Section
    doc.append(Paragraph("Individual Wrapped Analysis", styles['Heading3']))
    analysis_bullets = [
        "<b>League Summary Table:</b> A high-level overview of your rank, biggest fan, and other key metrics.",
        "<b>Compatibility Table:</b> Ranks league members by compatibility %.",
        "<b>Similarity Table:</b> Ranks league members by voting similarity %",
        "<b>Popularity Plot Analysis:</b> Visualizes the popularity of your song submissions."
    ]

    for bullet in analysis_bullets:
        doc.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;➤ {bullet}", styles['BodyText']))

    doc.append(PageBreak())

    # Add Superlatives Page
    doc.append(Paragraph(
        "<font color='black'>Lets Get Into</font><br/><br/><font color='#1DB954'>Superlatives</font>",
        styles['Title']
    ))

    doc.append(Spacer(1, 50))  # Add space before image

    # Path to the cover image
    superlatives_cover_image_path = os.path.join(base_path, "meme_pics", "superlatives_cover.png")

    # Check if the image exists before adding it
    if os.path.exists(cover_image_path):
        doc.append(Image(superlatives_cover_image_path, width=300, height=400))

    doc.append(PageBreak())

    # 🏆 Identify Rounds Missed by Each Competitor
    # Step 1: Group votes by Spotify URI and Round ID to get total votes per submission per round
    grouped_votes = votes.groupby(['Spotify URI', 'Round ID'])['Points Assigned'].sum().reset_index()

    # Step 2: Merge grouped_votes with submissions to get Submitter ID and avoid mapping issues
    grouped_votes = grouped_votes.merge(
        submissions[['Spotify URI', 'Submitter ID', 'Round ID']],
        on=['Spotify URI', 'Round ID'],
        how='left'
    )

    # Step 3: Identify rounds where each competitor did not vote
    voter_participation = votes.groupby(['Voter ID', 'Round ID']).size().reset_index(name='Vote Count')
    all_rounds = votes['Round ID'].unique()

    missed_rounds = {
        voter: set(all_rounds) - set(voter_participation[voter_participation['Voter ID'] == voter]['Round ID'])
        for voter in voter_participation['Voter ID'].unique()
    }

    # Step 4: Filter out votes from competitors who missed voting in those rounds
    filtered_votes = grouped_votes[~grouped_votes.apply(
        lambda row: row['Round ID'] in missed_rounds.get(row['Submitter ID'], set()), axis=1
    )]

    # Step 5: Calculate total votes received for each competitor after filtering
    competitor_total_votes_received = (
        filtered_votes.groupby('Submitter ID')['Points Assigned'].sum().reset_index()
            .rename(columns={'Submitter ID': 'ID', 'Points Assigned': 'Total Votes'})
    )

    # Ensure all competitors are included (even if they received no votes)
    competitor_total_votes_received = competitors.merge(competitor_total_votes_received, on='ID', how='left').fillna(0)

    # Step 6: Sort by total votes and build competitor_ranks
    sorted_competitors = competitor_total_votes_received.sort_values(by='Total Votes', ascending=False)
    competitor_ranks = {row.ID: rank + 1 for rank, row in enumerate(sorted_competitors.itertuples())}

    # Debugging output
    print(sorted_competitors[['Name', 'Total Votes']])

    # 🏆 Most Popular (Top 3 Competitors by Total Votes)
    doc.append(Paragraph("Most Popular", styles['Heading2']))

    # Reset index to ensure ranks are correct
    top_competitors = sorted_competitors.head(3).reset_index()

    top_names = top_competitors['Name'].tolist()
    top_votes = top_competitors['Total Votes'].astype(int).tolist()

    # Create podium labels
    labels = [f"{name}\nVotes: {votes}" for name, votes in zip(top_names, top_votes)]

    # Generate Podium Visual
    create_podium_visual(top_votes, labels, os.path.join(output_dir, "most_popular_podium.png"))
    doc.append(Image(os.path.join(output_dir, "most_popular_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins with fixed rank calculation
    for i, row in top_competitors.iterrows():
        rank = ordinal_suffix(i + 1)  # Rank is now simply 1, 2, 3 based on the loop index
        superlative_wins[row['ID']].append(f"Most Popular ({rank})")

    # Most Popular Table
    most_popular_table_data = [["Rank", "Name", "Total Votes"]] + [
        [i + 1, name, votes] for i, (name, votes) in enumerate(zip(top_names, top_votes))
    ]
    doc.append(create_table_with_borders(most_popular_table_data, col_widths=[50, 200, 100]))
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Most Popular")  # ✅ Add the meme image
    doc.append(PageBreak())

    # Most Likely to Lose Soo Badly Oof (Bottom 3 Competitors by Total Votes)
    doc.append(Paragraph("Most Likely to Lose Soo Badly Oof", styles['Heading2']))

    # Use sorted_competitors to find the bottom 3 competitors and reverse the order
    bottom_competitors = sorted_competitors.tail(3).iloc[::-1].reset_index()  # Reverse the order for the podium
    lowest_names = bottom_competitors['Name'].tolist()
    lowest_votes = bottom_competitors['Total Votes'].astype(int).tolist()

    # Generate podium visual with reversed order
    create_podium_visual(
        lowest_votes,
        [f"{name}\nVotes: {votes}" for name, votes in zip(lowest_names, lowest_votes)],
        os.path.join(output_dir, "most_likely_to_lose_podium.png")
    )

    # Insert podium visual into PDF
    doc.append(Image(os.path.join(output_dir, "most_likely_to_lose_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins (adjust rank based on reversed order)
    for i, row in bottom_competitors.iterrows():
        rank = ordinal_suffix(i + 1)  # Rank is simply 1, 2, 3 based on the loop index
        superlative_wins[row['ID']].append(f"Most Likely to Lose Soo Badly Oof ({rank})")

    # Create accompanying table
    lose_table_data = [["Rank", "Name", "Total Votes"]] + [
        [i + 1, name, votes] for i, (name, votes) in enumerate(zip(lowest_names, lowest_votes))
    ]

    # Format table
    lose_table = create_table_with_borders(lose_table_data, col_widths=[50, 200, 100])
    doc.append(lose_table)
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Most Likely to Lose Soo Badly Oof")  # ✅ Add the meme image
    doc.append(PageBreak())

    # Most Likely to Be Average as Hell (Middle 3 Competitors by Total Votes)
    doc.append(Paragraph("Most Likely to Be Average as Hell", styles['Heading2']))

    # Determine the number of competitors
    num_competitors = len(sorted_competitors)
    mid_index = num_competitors // 2  # Integer division to get middle index

    # Find the middle 3 competitors
    if num_competitors % 2 == 1:
        # Odd number of competitors, exact middle exists
        middle_competitors = sorted_competitors.iloc[[mid_index - 1, mid_index, mid_index + 1]].reset_index()
    else:
        # Even number of competitors, take the middle three
        middle_competitors = sorted_competitors.iloc[[mid_index - 1, mid_index, mid_index + 1]].reset_index()

    # Extract names and votes
    avg_names = middle_competitors['Name'].tolist()
    avg_votes = middle_competitors['Total Votes'].astype(int).tolist()

    # Generate podium visual
    create_podium_visual(
        avg_votes,
        [f"{name}\nVotes: {votes}" for name, votes in zip(avg_names, avg_votes)],
        os.path.join(output_dir, "most_likely_to_be_average_podium.png")
    )

    # ✅ Append winners to superlative_wins
    for i, row in middle_competitors.iterrows():
        rank = ordinal_suffix(i + 1)  # Rank is simply 1, 2, 3 based on the loop index
        superlative_wins[row['ID']].append(f"Most Likely to Be Average as Hell ({rank})")

    # Insert podium visual into PDF
    doc.append(Image(os.path.join(output_dir, "most_likely_to_be_average_podium.png"), width=400, height=300))

    # Create accompanying table
    avg_table_data = [["Rank", "Name", "Total Votes"]] + [
        [i + 1, name, votes] for i, (name, votes) in enumerate(zip(avg_names, avg_votes))
    ]

    # Format table
    avg_table = create_table_with_borders(avg_table_data, col_widths=[50, 200, 100])
    doc.append(avg_table)
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Most Likely to Be Average as Hell")  # ✅ Add the meme image
    doc.append(PageBreak())

    # 🎵 Best Performance (Top 3 Unique Song Submissions)
    doc.append(Paragraph("Best Performance", styles['Heading2']))

    top_songs = get_top_songs_by_votes(submissions, votes, top_n=3)

    # Extract song details for the top 3
    song_names = [song['Title'] for song in top_songs]
    song_votes = [song['Points Assigned'] for song in top_songs]
    submitters = [
        competitors.loc[competitors['ID'] == song['Submitter ID'], 'Name'].values[0]
        for song in top_songs
    ]
    artists = [song['Artist(s)'] for song in top_songs]

    # Create the podium visual
    labels = [f"{submitter}\n{title}" for submitter, title in zip(submitters, song_names)]
    create_podium_visual(song_votes, labels, os.path.join(output_dir, "best_performance_podium.png"))
    doc.append(Image(os.path.join(output_dir, "best_performance_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, song in enumerate(top_songs):
        rank = ordinal_suffix(i + 1)
        submitter_id = song['Submitter ID']
        superlative_wins[submitter_id].append(f"Best Performance ({rank})")

    # Create the table for Best Performance
    best_performance_table_data = [["Rank", "Name", "Song", "Artist(s)", "Votes"]] + [
        [i + 1, competitors.loc[competitors['ID'] == song['Submitter ID'], 'Name'].values[0],
         song['Title'], song['Artist(s)'], song['Points Assigned']]
        for i, song in enumerate(top_songs)
    ]
    doc.append(create_table_with_borders(best_performance_table_data, col_widths=[40, 120, 150, 150, 80]))
    doc.append(Spacer(1, 10))
    add_meme_image("Best Performance")
    doc.append(PageBreak())

    # 💬 Chatty Cathy (Top 3 by Comments)
    doc.append(Paragraph("Chatty Cathy ", styles['Heading2']))
    chatty_cathy = votes.groupby('Voter ID')['Comment'].count().nlargest(3)

    top_commenters = [competitors.loc[competitors['ID'] == voter, 'Name'].values[0] for voter in chatty_cathy.index]
    top_comment_counts = chatty_cathy.values
    labels = [f"{name}\nComments: {count}" for name, count in zip(top_commenters, top_comment_counts)]

    create_podium_visual(top_comment_counts, labels, os.path.join(output_dir, "chatty_cathy_podium.png"))
    doc.append(Image(os.path.join(output_dir, "chatty_cathy_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, voter_id in enumerate(chatty_cathy.index[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[voter_id].append(f"Chatty Cathy ({rank})")

    # Chatty Cathy Table
    chatty_table_data = [["Rank", "Name", "Total Comments"]] + [
        [i + 1, competitors.loc[competitors['ID'] == voter, 'Name'].values[0], count]
        for i, (voter, count) in enumerate(chatty_cathy.items())  # ✅ `.items()` fixes unpacking issue
    ]

    doc.append(create_table_with_borders(chatty_table_data, col_widths=[50, 200, 100]))
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Chatty Cathy")  # ✅ Add the meme image
    doc.append(PageBreak())

    # ✍️ The Author (Top 3 Longest Comments)
    doc.append(Paragraph("The Author", styles['Heading2']))
    votes['Comment Length'] = votes['Comment'].fillna('').str.len()
    longest_comments = votes.loc[
        votes.groupby('Voter ID')['Comment Length'].idxmax(), ['Voter ID', 'Comment Length', 'Comment']].nlargest(3,
                                                                                                                  'Comment Length')

    top_authors = [competitors.loc[competitors['ID'] == voter, 'Name'].values[0] for voter in
                   longest_comments['Voter ID']]
    top_lengths = longest_comments['Comment Length'].values
    top_comments = longest_comments['Comment'].values

    labels = [f"{name}\nCharacters: {length}" for name, length in zip(top_authors, top_lengths)]
    create_podium_visual(top_lengths, labels, os.path.join(output_dir, "the_author_podium.png"))
    doc.append(Image(os.path.join(output_dir, "the_author_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, row in enumerate(longest_comments.itertuples()):
        rank = ordinal_suffix(i + 1)
        voter_id = row._1  # Assuming the first column is Voter ID
        superlative_wins[voter_id].append(f"The Author ({rank})")

    # The Author Table
    author_table_data = [["Rank", "Name", "Comment Length", "Comment"]] + [
        [i + 1, name, length, comment]  # Include Rank, Name, Length, Comment
        for i, (name, comment, length) in enumerate(zip(top_authors, top_comments, top_lengths))
    ]

    # ✅ Create table with word-wrapped text in all cells
    doc.append(create_table_with_borders(author_table_data, col_widths=[50, 150, 100, 250]))
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("The Author")  # ✅ Add the meme image
    doc.append(PageBreak())

    # ✅ Calculate Average Spotify Popularity Per Competitor
    popularity_scores = {}
    for competitor_id in competitors['ID']:
        competitor_songs = submissions[submissions['Submitter ID'] == competitor_id]

        # Placeholder: Use a fixed value of 75 for all popularity scores
        #popularity_values = [75 for _ in range(len(competitor_songs))]

        popularity_values = [
            get_track_popularity(row['Spotify URI'], token) for _, row in competitor_songs.iterrows()
        ]
        if popularity_values:
            popularity_scores[competitor_id] = sum(popularity_values) / len(popularity_values)
        else:
            popularity_scores[competitor_id] = 0  # If no songs were submitted

    # ✅ Crowd Pleaser (Top 3 Competitors by Highest Avg Popularity)
    doc.append(Paragraph("Crowd Pleaser", styles['Heading2']))
    sorted_crowd_pleasers = sorted(popularity_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    crowd_pleaser_names = [competitors.loc[competitors['ID'] == comp[0], 'Name'].values[0] for comp in
                           sorted_crowd_pleasers]
    crowd_pleaser_popularity = [int(comp[1]) for comp in sorted_crowd_pleasers]

    create_podium_visual(
        crowd_pleaser_popularity,
        [f"{name}\nPopularity: {pop}" for name, pop in zip(crowd_pleaser_names, crowd_pleaser_popularity)],
        os.path.join(output_dir, "crowd_pleaser_podium.png")
    )

    doc.append(Image(os.path.join(output_dir, "crowd_pleaser_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, (competitor_id, _) in enumerate(sorted_crowd_pleasers[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[competitor_id].append(f"Crowd Pleaser ({rank})")

    # ✅ Crowd Pleaser Table
    table_data = [["Rank", "Name", "Avg Popularity"]] + [
        [i + 1, name, int(pop)] for i, (name, pop) in enumerate(zip(crowd_pleaser_names, crowd_pleaser_popularity))
    ]
    doc.append(create_table_with_borders(table_data, col_widths=[50, 200, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space

    # ✅ Crowd Pleaser Meme
    add_meme_image("Crowd Pleaser")

    doc.append(PageBreak())

    # ✅ Trend Setters (Top 3 Competitors by Lowest Avg Popularity)
    doc.append(Paragraph("Trend Setters", styles['Heading2']))
    sorted_trend_setters = sorted(popularity_scores.items(), key=lambda x: x[1])[:3]  # Lowest popularity

    trend_setter_names = [competitors.loc[competitors['ID'] == comp[0], 'Name'].values[0] for comp in
                          sorted_trend_setters]
    trend_setter_popularity = [int(comp[1]) for comp in sorted_trend_setters]

    create_podium_visual(
        trend_setter_popularity,
        [f"{name}\nPopularity: {pop}" for name, pop in zip(trend_setter_names, trend_setter_popularity)],
        os.path.join(output_dir, "trend_setters_podium.png")
    )

    doc.append(Image(os.path.join(output_dir, "trend_setters_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, (competitor_id, _) in enumerate(sorted_trend_setters[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[competitor_id].append(f"Trend Setter ({rank})")

    # ✅ Trend Setters Table
    table_data = [["Rank", "Name", "Avg Popularity"]] + [
        [i + 1, name, int(pop)] for i, (name, pop) in enumerate(zip(trend_setter_names, trend_setter_popularity))
    ]
    doc.append(create_table_with_borders(table_data, col_widths=[50, 200, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space

    # ✅ Trend Setters Meme
    add_meme_image("Trend Setter")

    doc.append(PageBreak())

    # ✅ Compute Compatibility Scores (Ensure IDs Are Used)
    compat_scores = calculate_compatibility_scores(votes, competitors, submissions)

    # ✅ Ensure compat_scores stores IDs, not names
    fixed_compat_scores = {}
    for p1, scores in compat_scores.items():
        if p1 in competitors['Name'].values:  # If p1 is a name, convert it to an ID
            p1_id = competitors.loc[competitors['Name'] == p1, 'ID'].values[0]
        else:
            p1_id = p1  # Already an ID

        fixed_compat_scores[p1_id] = {}

        for p2, data in scores.items():
            if p2 in competitors['Name'].values:  # Convert p2 to an ID if needed
                p2_id = competitors.loc[competitors['Name'] == p2, 'ID'].values[0]
            else:
                p2_id = p2  # Already an ID

            fixed_compat_scores[p1_id][p2_id] = data["compatibility_score"]

    # ✅ Now use fixed_compat_scores in the sorting
    unique_compatibility = set()
    sorted_compatibility = sorted(
        [
            ((p1, p2), score)
            for p1, scores in fixed_compat_scores.items()
            for p2, score in scores.items() if p1 != p2
        ],
        key=lambda x: x[1],
        reverse=True
    )

    filtered_compatibility = []
    for (p1, p2), score in sorted_compatibility:
        if (p2, p1) not in unique_compatibility:
            unique_compatibility.add((p1, p2))
            filtered_compatibility.append(((p1, p2), score))
        if len(filtered_compatibility) == 3:  # Keep only top 3 pairs
            break

    # ✅ Function to safely fetch competitor names from IDs
    def get_competitor_name(competitor_id, competitors):
        filtered = competitors.loc[competitors['ID'] == competitor_id, 'Name']
        if not filtered.empty:
            return filtered.values[0]  # ✅ Extract name safely

        print(f"⚠️ Warning: Competitor ID {competitor_id} not found in competitors DataFrame!")  # ✅ Debugging
        return "Unknown"

    # ✅ Convert IDs to names when displaying results
    most_compatible_pairs = []
    for pair, score in filtered_compatibility:
        print(f"🔍 Debug: Looking up IDs {pair}")  # ✅ Print IDs before lookup

        name1 = get_competitor_name(pair[0], competitors)  # ✅ Convert ID to Name
        name2 = get_competitor_name(pair[1], competitors)  # ✅ Convert ID to Name

        most_compatible_pairs.append((f"{name1} & {name2}", f"{score:.0f}%"))

    print(f"🔍 Debug: most_compatible_pairs = {most_compatible_pairs}")  # ✅ Debugging Output

    # ✅ Add "Most Compatible" Superlative
    doc.append(Paragraph("Most Compatible (Most Likely to be in Kahoots)", styles['Heading2']))
    create_podium_visual(
        [float(score[:-1]) for _, score in most_compatible_pairs],  # Convert % to float
        [f"{name.split(' & ')[0]}\n&\n{name.split(' & ')[1]}\n{score}" for name, score in most_compatible_pairs],
        os.path.join(output_dir, "most_compatible_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "most_compatible_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, (pair, _) in enumerate(filtered_compatibility[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[pair[0]].append(f"Most Compatible ({rank})")
        superlative_wins[pair[1]].append(f"Most Compatible ({rank})")

    # ✅ Most Compatible Table
    compatibility_table_data = [["Rank", "Names", "Compatibility %"]] + [
        [i + 1, name, score] for i, (name, score) in enumerate(most_compatible_pairs)
    ]
    doc.append(create_table_with_borders(compatibility_table_data, col_widths=[50, 250, 100]))
    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space

    # ✅ Add Meme Image
    add_meme_image("Most Compatible")
    doc.append(PageBreak())

    # 🎭 **Least Compatible (Bottom 3 Compatibility Scores)**
    doc.append(Paragraph("Least Compatible", styles['Heading2']))

    # ✅ Extract Bottom 3 Compatibility Pairs
    sorted_least_compatible = sorted_compatibility[-3:]  # Take the lowest 3 pairs

    # ✅ Format "Least Compatible" Pairs
    least_compatible_pairs = []
    for pair, score in sorted_least_compatible:
        name1 = get_competitor_name(pair[0], competitors)
        name2 = get_competitor_name(pair[1], competitors)
        least_compatible_pairs.append((f"{name1} & {name2}", f"{score:.0f}%"))

    print(f"🔍 Debug: least_compatible_pairs = {least_compatible_pairs}")  # ✅ Debugging Output

    # ✅ Generate Podium Visual
    create_podium_visual(
        [float(score[:-1]) for _, score in least_compatible_pairs],
        [f"{name1}\n&\n{name2}\n{score}" for name, score in least_compatible_pairs
         for name1, name2 in [name.split(" & ")]],  # ✅ Safely extract names
        os.path.join(output_dir, "least_compatible_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "least_compatible_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, (pair, _) in enumerate(sorted_least_compatible[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[pair[0]].append(f"Least Compatible ({rank})")
        superlative_wins[pair[1]].append(f"Least Compatible ({rank})")

    # ✅ Create Least Compatible Table
    least_compatible_table_data = [["Rank", "Names", "Compatibility %"]] + [
        [i + 1, name, score] for i, (name, score) in enumerate(least_compatible_pairs)
    ]
    doc.append(create_table_with_borders(least_compatible_table_data, col_widths=[50, 250, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space

    # ✅ Add Meme Image
    add_meme_image("Least Compatible")
    doc.append(PageBreak())

    # ✅ Compute Voting Similarity Before Superlatives
    vote_similarity = {}
    player_votes = votes.groupby('Voter ID')['Spotify URI'].apply(set).to_dict()

    for p1, votes1 in player_votes.items():
        vote_similarity[p1] = {}
        for p2, votes2 in player_votes.items():
            if p1 == p2:
                continue
            intersection = len(votes1 & votes2)
            union = len(votes1 | votes2)
            similarity_score = (intersection / union) * 100 if union > 0 else 0
            vote_similarity[p1][p2] = similarity_score

    # ✅ Extract Top 3 Most Similar Pairs (Remove Duplicate Pairs)
    unique_similarity = set()
    filtered_similarity = []

    sorted_similarity = sorted(
        [
            ((p1, p2), similarity_score)
            for p1, scores in vote_similarity.items()
            for p2, similarity_score in scores.items() if p1 != p2
        ],
        key=lambda x: x[1],
        reverse=True
    )

    for (p1, p2), score in sorted_similarity:
        if (p2, p1) not in unique_similarity:  # ✅ Ensure we don’t duplicate (A, B) & (B, A)
            unique_similarity.add((p1, p2))
            filtered_similarity.append(((p1, p2), score))
        if len(filtered_similarity) == 3:  # ✅ Keep only the top 3 unique pairs
            break

    # ✅ Format "Most Similar" Pairs
    most_similar_pairs = []
    for pair, score in filtered_similarity:
        name1 = get_competitor_name(pair[0], competitors)
        name2 = get_competitor_name(pair[1], competitors)
        most_similar_pairs.append((f"{name1} & {name2}", f"{score:.0f}%"))

    print(f"🔍 Debug: most_similar_pairs = {most_similar_pairs}")  # ✅ Debugging Output

    # 🎯 **Add "Most Similar" Superlative**
    doc.append(Paragraph("Most Similar", styles['Heading2']))

    # ✅ Generate Podium Visual
    create_podium_visual(
        [float(score[:-1]) for _, score in most_similar_pairs],
        [f"{name.split(' & ')[0]}\n&\n{name.split(' & ')[1]}\n{score}" for name, score in most_similar_pairs],
        os.path.join(output_dir, "most_similar_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "most_similar_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, (pair, _) in enumerate(filtered_similarity[:3]):
        rank = ordinal_suffix(i + 1)
        superlative_wins[pair[0]].append(f"Most Similar ({rank})")
        superlative_wins[pair[1]].append(f"Most Similar ({rank})")

    # ✅ Create Table
    similarity_table_data = [["Rank", "Names", "Voting Similarity %"]] + [
        [i + 1, name, score] for i, (name, score) in enumerate(most_similar_pairs)
    ]
    doc.append(create_table_with_borders(similarity_table_data, col_widths=[50, 250, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    # ✅ Add Meme Image
    add_meme_image("Most Similar")
    doc.append(PageBreak())

    # ✅ Extract Unique Least Similar Pairs (Remove Duplicate Pairs)
    unique_similarity = set()
    filtered_similarity = []

    # ✅ Sort by lowest similarity percentage (ascending order)
    sorted_similarity = sorted(
        [
            ((p1, p2), similarity_score)
            for p1, scores in vote_similarity.items()
            for p2, similarity_score in scores.items() if p1 != p2
        ],
        key=lambda x: x[1]  # ✅ Sort by similarity score (ascending)
    )

    # ✅ Filter unique pairs
    for (p1, p2), score in sorted_similarity:
        if (p2, p1) not in unique_similarity:  # ✅ Ensure we don’t duplicate (A, B) & (B, A)
            unique_similarity.add((p1, p2))
            filtered_similarity.append(((p1, p2), score))
        if len(filtered_similarity) == 3:  # ✅ Keep only the bottom 3 unique pairs
            break

    # 🎭 **Least Similar (Bottom 3 Voting Similarity Scores)**
    doc.append(Paragraph("Least Similar", styles['Heading2']))

    # ✅ Extract the bottom 3 least similar pairs (lowest similarity %)
    sorted_least_similar = filtered_similarity[:3]  # ✅ Select the 3 lowest similarity scores

    # ✅ Format "Least Similar" Pairs
    least_similar_pairs = []
    for pair, score in sorted_least_similar:
        name1 = get_competitor_name(pair[0], competitors)
        name2 = get_competitor_name(pair[1], competitors)
        least_similar_pairs.append((f"{name1} & {name2}", f"{score:.0f}%"))

    print(f"🔍 Debug: least_similar_pairs = {least_similar_pairs}")  # ✅ Debugging Output

    # ✅ Generate Podium Visual (flipped so that 1st = lowest similarity)
    create_podium_visual(
        [float(score[:-1]) for _, score in least_similar_pairs],  # ✅ Convert % to float
        [f"{name1}\n&\n{name2}\n{score}" for name, score in least_similar_pairs
         for name1, name2 in [name.split(" & ")]],  # ✅ Safely extract names
        os.path.join(output_dir, "least_similar_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "least_similar_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins with correct ranks
    for i, (pair, _) in enumerate(sorted_least_similar):
        rank = ordinal_suffix(i + 1)
        superlative_wins[pair[0]].append(f"Least Similar ({rank})")
        superlative_wins[pair[1]].append(f"Least Similar ({rank})")

    # ✅ Create Least Similar Table
    least_similar_table_data = [["Rank", "Names", "Voting Similarity %"]] + [
        [i + 1, name, score] for i, (name, score) in enumerate(least_similar_pairs)
    ]
    doc.append(create_table_with_borders(least_similar_table_data, col_widths=[50, 250, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space

    # ✅ Add Meme Image
    add_meme_image("Least Similar")
    doc.append(PageBreak())

    # 🏆 **Most Likely to Vote First & Last**
    doc.append(Paragraph("Most Likely to Vote First", styles['Heading2']))

    # ✅ Step 1: Extract unique votes for each voter per round (based on the earliest timestamp)
    unique_votes = votes.sort_values(by='Created').drop_duplicates(subset=['Round ID', 'Voter ID'], keep='first')

    # ✅ Step 2: Rank voters by submission time within each round
    unique_votes['Rank'] = unique_votes.groupby('Round ID')['Created'].rank(method='first')

    # ✅ Step 3: Calculate average rank for each competitor
    avg_voting_speed_rank = unique_votes.groupby('Voter ID')['Rank'].mean().reset_index()
    avg_voting_speed_rank.columns = ['Voter ID', 'Avg Rank']

    # ✅ Step 4: Determine the superlatives
    most_likely_first = avg_voting_speed_rank.nsmallest(3, 'Avg Rank')
    most_likely_last = avg_voting_speed_rank.nlargest(3, 'Avg Rank')

    # ✅ Step 5: Convert avg_voting_speed_rank to a dictionary for easy lookup
    voting_speed_ranks = {
        row['Voter ID']: row['Avg Rank'] for _, row in avg_voting_speed_rank.iterrows()
    }

    # 🏆 **Most Likely to Vote First**
    first_names = [get_competitor_name(row['Voter ID'], competitors) for _, row in most_likely_first.iterrows()]
    first_ranks = [ordinal_suffix(int(round(row['Avg Rank']))) for _, row in most_likely_first.iterrows()]

    # ✅ Generate Podium Visual for "Most Likely to Vote First"
    create_podium_visual(
        [float(rank.rstrip('stndrdth')) for rank in first_ranks],  # Use numeric rank for plotting
        [f"{name}\nAvg Rank: {rank} to vote" for name, rank in zip(first_names, first_ranks)],
        os.path.join(output_dir, "most_likely_first_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "most_likely_first_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, row in enumerate(most_likely_first.itertuples()):
        rank = ordinal_suffix(i + 1)
        voter_id = row._1  # Assuming Voter ID is in the first column
        superlative_wins[voter_id].append(f"Most Likely to Vote First ({rank})")

    # ✅ Create Table for "Most Likely to Vote First"
    first_table_data = [["Rank", "Name", "Avg. Voting Speed Rank"]] + [
        [i + 1, name, rank] for i, (name, rank) in enumerate(zip(first_names, first_ranks))
    ]
    doc.append(create_table_with_borders(first_table_data, col_widths=[50, 250, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Most Likely to Vote First")
    doc.append(PageBreak())

    # 🏆 **Most Likely to Vote Last**
    doc.append(Paragraph("Most Likely to Vote Last", styles['Heading2']))

    last_names = [get_competitor_name(row['Voter ID'], competitors) for _, row in most_likely_last.iterrows()]
    last_ranks = [ordinal_suffix(int(round(row['Avg Rank']))) for _, row in most_likely_last.iterrows()]

    # ✅ Generate Podium Visual for "Most Likely to Vote Last"
    create_podium_visual(
        [float(rank.rstrip('stndrdth')) for rank in last_ranks],  # Use numeric rank for plotting
        [f"{name}\nAvg Rank: {rank} to vote" for name, rank in zip(last_names, last_ranks)],
        os.path.join(output_dir, "most_likely_last_podium.png")
    )
    doc.append(Image(os.path.join(output_dir, "most_likely_last_podium.png"), width=400, height=300))

    # ✅ Append winners to superlative_wins
    for i, row in enumerate(most_likely_last.itertuples()):
        rank = ordinal_suffix(i + 1)
        voter_id = row._1
        superlative_wins[voter_id].append(f"Most Likely to Vote Last ({rank})")

    # ✅ Create Table for "Most Likely to Vote Last"
    last_table_data = [["Rank", "Name", "Avg. Voting Speed Rank"]] + [
        [i + 1, name, rank] for i, (name, rank) in enumerate(zip(last_names, last_ranks))
    ]
    doc.append(create_table_with_borders(last_table_data, col_widths=[50, 250, 100]))

    doc.append(Spacer(1, 10))  # ✅ Add 10 units of vertical space
    add_meme_image("Most Likely to Vote Last")
    doc.append(PageBreak())

    # Individual Analysis Pages
    # Add Individual Analysis Intro Page
    doc.append(Paragraph(
        "<font color='black'>Lets Get Into</font><br/><br/><font color='#1DB954'>Individual Wrapped<br/><br/>Analysis</font>",
        styles['Title']
    ))

    doc.append(Spacer(1, 50))  # Add space before image

    # Path to the cover image
    superlatives_cover_image_path = os.path.join(base_path, "meme_pics", "wrapped_cover.png")

    # Check if the image exists before adding it
    if os.path.exists(cover_image_path):
        doc.append(Image(superlatives_cover_image_path, width=300, height=400))

    doc.append(PageBreak())

    # ✅ Precompute overall rankings

    # 🏆 Calculate Total Votes for Each Competitor
    competitor_total_votes = (
        votes.groupby('Voter ID')['Points Assigned']
            .sum()
            .reset_index()
            .rename(columns={'Voter ID': 'ID', 'Points Assigned': 'Total Votes'})
    )

    # ✅ Compute Average Popularity for Each Competitor
    competitor_popularity = {}
    for competitor_id in competitors['ID']:
        competitor_songs = submissions[submissions['Submitter ID'] == competitor_id]

        # Placeholder: Use a fixed value of 75 for all popularity scores
        #popularity_values = [75 for _ in range(len(competitor_songs))]

        popularity_values = [
            get_track_popularity(row['Spotify URI'], token) for _, row in competitor_songs.iterrows()
        ]
        avg_popularity = sum(popularity_values) / len(popularity_values) if popularity_values else 0
        competitor_popularity[competitor_id] = avg_popularity

    # ✅ Rank competitors by popularity
    ranked_popularity = sorted(competitor_popularity.items(), key=lambda x: x[1], reverse=True)
    popularity_ranks = {comp_id: rank + 1 for rank, (comp_id, _) in enumerate(ranked_popularity)}


    # ✅ Individual Analysis Pages
    for competitor in sorted_competitors['ID']:
        name = competitors.loc[competitors['ID'] == competitor, 'Name'].values[0]
        doc.append(Paragraph(f"{name}'s Wrapped Analysis", styles['Heading2']))

        # 🎯 **League Summary Section**
        doc.append(Paragraph("League Summary", styles['Heading3']))

        # ✅ Rank in the League with Correct Total Number of Participants
        total_competitors = competitors['ID'].nunique()
        rank = competitor_ranks.get(competitor, "N/A")

        if rank != "N/A":
            formatted_rank = f"{rank}/{total_competitors}"
        else:
            formatted_rank = "N/A"

        # ✅ Biggest Fan by Percentage of Total Votes Given
        received_votes = votes[
            votes['Spotify URI'].isin(submissions[submissions['Submitter ID'] == competitor]['Spotify URI'])
        ]
        received_votes = received_votes[received_votes['Voter ID'] != competitor]  # Exclude self-votes

        # Total votes given by each voter
        total_votes_by_voter = votes.groupby('Voter ID')['Points Assigned'].sum()

        # Votes given to this competitor by each voter
        votes_given_to_competitor = received_votes.groupby('Voter ID')['Points Assigned'].sum()

        # Calculate percentage of total votes given to this competitor by each voter
        fan_percentages = (votes_given_to_competitor / total_votes_by_voter).fillna(0) * 100

        if not fan_percentages.empty:
            biggest_fan_id = fan_percentages.idxmax()
            biggest_fan_name = competitors.loc[competitors['ID'] == biggest_fan_id, 'Name'].values[0] \
                if biggest_fan_id in competitors['ID'].values else "N/A"
        else:
            biggest_fan_name = "N/A"

        # ✅ Convert compat_scores to use competitor IDs
        fixed_compat_scores = {}
        for p1, scores in compat_scores.items():
            p1_id = competitors.loc[competitors['Name'] == p1, 'ID'].values[0] if p1 in competitors[
                'Name'].values else p1
            fixed_compat_scores[p1_id] = {}

            for p2, data in scores.items():
                p2_id = competitors.loc[competitors['Name'] == p2, 'ID'].values[0] if p2 in competitors[
                    'Name'].values else p2
                fixed_compat_scores[p1_id][p2_id] = data["compatibility_score"]

        # ✅ Find the most compatible person for each competitor
        if competitor in fixed_compat_scores:
            most_compatible_id = max(fixed_compat_scores[competitor], key=fixed_compat_scores[competitor].get)
            most_compatible_name = competitors.loc[competitors['ID'] == most_compatible_id, 'Name'].values[0]
        else:
            most_compatible_name = "N/A"

        # ✅ Debugging Output
        #print(f"🔍 Debug: {competitor} is most compatible with {most_compatible_name}")

        # ✅ Most Similar Person
        if competitor in vote_similarity and vote_similarity[competitor]:
            most_similar_person = max(vote_similarity[competitor], key=vote_similarity[competitor].get)
            most_similar_name = competitors.loc[competitors['ID'] == most_similar_person, 'Name'].values[0] \
                if most_similar_person in competitors['ID'].values else "N/A"
        else:
            most_similar_name = "N/A"

        # ✅ Average Song Popularity (rounded to nearest integer)
        avg_popularity = round(competitor_popularity.get(competitor, 0))

        # ✅ Popularity Rank with Total Number of Competitors
        total_competitors = len(popularity_ranks)
        popularity_rank = popularity_ranks.get(competitor, "N/A")

        if popularity_rank != "N/A":
            popularity_rank = f"{int(popularity_rank)}/{total_competitors}"  # Round and convert to int for clean output
        else:
            popularity_rank = "N/A"

        # Get the song the competitor voted the most for
        favorite_song_data = most_votes_cast(votes, submissions).get(competitor, {})

        if favorite_song_data:
            song_uri = favorite_song_data.get("Spotify URI", None)
            votes_casted = favorite_song_data.get("Votes", 0)

            #print(f"🔍 Debug: Competitor {competitor} - Favorite Song URI: {song_uri}, Votes: {votes_casted}")

            if song_uri:
                # Ensure we match only the track ID (strip potential "spotify:track:" prefix)
                track_id = song_uri.split(":")[-1]

                # Lookup song details using cleaned Spotify URI
                song_entry = submissions.loc[submissions['Spotify URI'].str.endswith(track_id, na=False)]

                if not song_entry.empty:
                    song_title = song_entry['Title'].values[0]
                    artist_names = song_entry['Artist(s)'].values[0]  # Assuming 'Artist' column exists

                    # Format the output
                    favorite_song_text = f"{song_title} - {artist_names} ({votes_casted} votes)"
                else:
                    print(f"⚠️ Warning: No match found for {track_id} in submissions!")
                    favorite_song_text = "Unknown Song"
            else:
                favorite_song_text = "N/A"
        else:
            favorite_song_text = "N/A"

        # ✅ Compute the competitor's voting speed rank
        voting_speed_rank = voting_speed_ranks.get(competitor, "N/A")
        if voting_speed_rank != "N/A":
            if voting_speed_rank != "N/A":
                voting_speed_rank = f"{int(round(voting_speed_rank))}/{total_competitors}"
            else:
                voting_speed_rank = "N/A"

        league_summary_data = [
            ["Data Point", "Value"],
            ["Rank", formatted_rank],
            ["Biggest Fan", biggest_fan_name],
            ["Most Compatible", most_compatible_name],
            ["Most Similar", most_similar_name],
            ["Avg. Song Popularity", f"{round(avg_popularity)}"],
            ["Avg. Song Popularity Rank", popularity_rank],
            ["Your Favorite Song", f"{favorite_song_text}"],
            ["Voting Speed Rank", voting_speed_rank]
        ]

        # 🏅 Add Superlatives Won
        if superlative_wins[competitor]:
            superlative_list = "\n".join([f"➤ {win}" for win in superlative_wins[competitor]])
        else:
            superlative_list = "➤ N/A lmao"

        league_summary_data.append(["Superlatives Won", superlative_list])

        # ✅ Create table with text wrapping in all cells
        league_summary_table = create_table_with_borders(league_summary_data, col_widths=[150, 300])
        doc.append(league_summary_table)
        doc.append(Spacer(1, 10))  # Add some space below the table

        doc.append(Paragraph("Who are you most compatible with?", styles['Heading3']))

        # Compute compatibility scores
        compat_scores = calculate_compatibility_scores(votes, competitors, submissions)

        if name in compat_scores:
            table_data = [["Rank", "Name", "% Votes Given", "% Votes Received", "Compatibility %"]]

            # ✅ Sort by compatibility % in descending order
            sorted_scores = sorted(
                compat_scores[name].items(), key=lambda x: x[1]["compatibility_score"], reverse=True
            )

            for i, (other_name, score_data) in enumerate(sorted_scores):
                percent_given = score_data["percent_given"]
                percent_other_given = score_data["percent_other_given"]
                compatibility_score = score_data["compatibility_score"]
                table_data.append([
                    i + 1, other_name, f"{percent_given:.2f}%", f"{percent_other_given:.2f}%",
                    f"{compatibility_score:.2f}%"
                ])

            # Apply table styling
            table = Table(table_data, colWidths=[40, 120, 80, 80, 80])  # Slightly smaller columns
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for header
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Regular font for other rows
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # ⬅️ **Even Smaller Font (6pt)**
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # ⬅️ **Minimal cell padding**
                ('TOPPADDING', (0, 0), (-1, -1), 0),  # ⬅️ **Minimal cell padding**
                ('BACKGROUND', (0, 1), (-1, -1), colors.honeydew),  # Data row background color
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),  # **Thinner grid lines**
            ]))
            doc.append(table)
            #doc.append(Spacer(1, 15))  # Add spacing after the table
            doc.append(PageBreak())

        # ✅ Compute Voting Similarity Scores
        doc.append(Paragraph("Who voted most similarly to you?", styles['Heading3']))

        # Extract votes for each player (as a set of unique Spotify URIs)
        player_votes = votes.groupby('Voter ID')['Spotify URI'].apply(set).to_dict()

        if competitor in player_votes:
            similarity_scores = []
            competitor_votes = player_votes[competitor]  # Get the set of songs voted for

            for other_player, other_votes in player_votes.items():
                if competitor == other_player:
                    continue  # Skip self

                # Compute Jaccard Similarity = (Intersection / Union)
                intersection = len(competitor_votes & other_votes)
                union = len(competitor_votes | other_votes)

                similarity = (intersection / union) * 100 if union > 0 else 0  # Handle division by zero
                similarity_scores.append((other_player, similarity))

            # Sort scores in descending order
            similarity_scores.sort(key=lambda x: x[1], reverse=True)

            # Convert player IDs to names
            similarity_data = [["Rank", "Name", "Voting Similarity %"]] + [
                [i + 1, competitors.loc[competitors['ID'] == other_id, 'Name'].values[0], f"{similarity:.2f}%"]
                for i, (other_id, similarity) in enumerate(similarity_scores)
            ]

            # ✅ Create and append the similarity table
            similarity_table = Table(similarity_data, colWidths=[50, 200, 100])
            similarity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BACKGROUND', (0, 1), (-1, -1), colors.honeydew),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
            ]))

            doc.append(similarity_table)
            doc.append(Spacer(1, 15))  # Add spacing after the table


        # Move to new page for better formatting
        doc.append(PageBreak())

        # Add new page title
        doc.append(Paragraph("How popular was the music you submitted?", styles['Heading3']))

        # Collect popularity & performance data
        popularity_data = []
        for _, row in submissions[submissions['Submitter ID'] == competitor].iterrows():
            # Placeholder
            #popularity=75
            popularity = get_track_popularity(row['Spotify URI'], token)  # Fetch real popularity data

            # ✅ Fix: Only count votes for THIS competitor's submission
            song_votes = votes[
                (votes['Spotify URI'] == row['Spotify URI']) & (votes['Round ID'] == row['Round ID'])
                ]['Points Assigned'].sum()

            if popularity is not None:
                popularity_data.append({'Song': row['Title'], 'Popularity': popularity, 'Votes': song_votes})

        if popularity_data:
            # ✅ Updated: Generate a better-sized plot with axis borders & fixed x-axis
            plot_popularity_chart(
                popularity_data,
                os.path.join(output_dir, f"popularity_{competitor}.png")
            )

            # Append the larger image to the new page
            doc.append(Image(os.path.join(output_dir, f"popularity_{competitor}.png"), width=500, height=300))

        doc.append(PageBreak())  # Ensure a clean page break after the plot

    def add_page_number(canvas, doc):
        """Adds a page number to the bottom center of each page."""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont("Helvetica", 10)  # Font and size
        canvas.drawCentredString(letter[0] / 2, 20, text)  # Position at the bottom center

    # ✅ Modify `SimpleDocTemplate` to use custom footer
    pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    pdf_doc.build(doc, onFirstPage=add_page_number, onLaterPages=add_page_number)

    print(f"✅ PDF report saved to {pdf_path}")


# Get default styles
styles = getSampleStyleSheet()
styles["Normal"].alignment = TA_LEFT  # Left-align text for better readability


def create_table_with_borders(data, col_widths=None):
    """Creates a formatted table with word wrapping and multi-line support, ensuring header styling."""
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.whitesmoke,
        alignment=0,  # Center-align header text
    )

    wrapped_data = []
    for i, row in enumerate(data):
        wrapped_row = []
        for cell in row:
            style = header_style if i == 0 else styles["Normal"]  # Apply header style to the first row
            if isinstance(cell, str) and "<br/>" in cell:
                wrapped_row.append(Paragraph(cell, style))
            else:
                wrapped_row.append(Paragraph(str(cell), style))
        wrapped_data.append(wrapped_row)

    table = Table(wrapped_data, colWidths=col_widths)
    table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Grey background for the header
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Regular font for non-header rows
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.black)
        ])
    )
    return table







