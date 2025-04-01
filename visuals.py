import matplotlib.pyplot as plt
import numpy as np
import os
from adjustText import adjust_text
import matplotlib.pyplot as plt


def create_podium_visual(data, labels, filename):
    """Generates a podium visual with consistent text spacing for rankings."""

    fig, ax = plt.subplots(figsize=(6, 4))

    # Ensure consistent height scaling
    max_height = max(data) if max(data) > 0 else 1  # Prevent divide by zero
    heights = [data[1], data[0], data[2]]  # Adjust order: 2nd, 1st, 3rd
    colors = ['#C0C0C0', '#FFD700', '#CD7F32']  # Silver, Gold, Bronze
    x_pos = [0, 1, 2]

    bars = ax.bar(x_pos, heights, color=colors, tick_label=['2nd', '1st', '3rd'], width=1.0, linewidth=0)

    # Fixed text spacing - ensures consistent gap between bars and labels
    text_offset = max_height * 0.05  # Controls how far text appears above bars

    for i, bar in enumerate(bars):
        corrected_index = [1, 0, 2][i]  # Fix label order
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + text_offset,  # Uniform spacing from bar top
            labels[corrected_index],
            ha='center',
            fontsize=10,
            color='black',
            wrap=True  # Wrap long text to avoid excessive stretching
        )

    # Standardize Y-axis scale to maintain consistency across podiums
    ax.set_ylim(0, max_height * 1.3)  # Keep extra space above tallest bar

    # Remove axes and labels for a clean look
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['2nd', '1st', '3rd'])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    plt.savefig(filename, transparent=True, bbox_inches='tight')
    plt.close()


def plot_popularity_chart(popularity_data, filename):
    """Plots a scatterplot of Spotify popularity vs. relative performance with smart label placement."""
    if not popularity_data:
        print("⚠️ No popularity data available to plot.")
        return

    # Extract values
    x_vals = [entry["Popularity"] for entry in popularity_data]
    y_vals = [entry["Votes"] for entry in popularity_data]  # Relative performance
    labels = [f"{entry['Song']} (Votes: {entry['Votes']})" for entry in popularity_data]

    # ✅ Normalize votes to make y-axis a relative scale (0 to 1.1)
    max_votes = max(y_vals) if y_vals else 1  # Avoid division by zero
    y_vals = [votes / max_votes for votes in y_vals]  # Normalize to 0-1 range

    # ✅ Fixed aspect ratio (Prevents stretching)
    fig, ax = plt.subplots(figsize=(6, 4))

    # ✅ Set fixed axis limits
    ax.set_xlim(0, 100)  # Spotify Popularity always 0-100
    ax.set_ylim(0, 1.1)  # Relative Performance from 0 to 1.1

    # ✅ Add black axes at x=0, y=0 for clarity
    ax.axhline(y=0, color='black', linewidth=1)
    ax.axvline(x=0, color='black', linewidth=1)

    # Plot scatter points
    scatter = ax.scatter(x_vals, y_vals, color="#1DB954", s=80, edgecolors="black")

    # ✅ Smart label placement to avoid overlap
    texts = []
    for i, txt in enumerate(labels):
        text = ax.annotate(
            txt, (x_vals[i], y_vals[i]), fontsize=8, ha='center', va='center'
        )
        texts.append(text)

    # ✅ Adjust label positions to avoid overlap
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=0.8))

    # ✅ Minimalist design (remove extra borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Labels
    ax.set_xlabel("Spotify Popularity (0-100)")
    ax.set_ylabel("Relative Performance (0-1)")

    # Save plot
    plt.tight_layout()
    plt.savefig(filename, dpi=300, transparent=True, bbox_inches='tight')
    plt.close()



