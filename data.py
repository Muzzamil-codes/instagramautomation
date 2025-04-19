import csv
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

def update_all_posts(csv_path):
    # Read all rows from CSV
    with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        print("CSV is empty.")
        return

    header = rows[0]
    expected_header = ['PostURL', 'ID', 'ShowerThought', 'VideoViews', 'Likes', 'Comments', 'Saves', 'shares', 'EngagementRate']
    if header != expected_header:
        print("CSV header format is incorrect.")
        return

    # Process each row (skip header)
    for i in range(1, len(rows)):
        row = rows[i]
        if len(row) < 9:
            print(f"Skipping row {i}: insufficient columns.")
            continue

        media_id = row[1].strip()
        if not media_id:
            print(f"Skipping row {i}: empty ID.")
            continue

        # Fetch metrics from API
        url = f"https://graph.facebook.com/v22.0/{media_id}/insights"
        params = {
            'metric': 'saved,views,likes,comments,shares',
            'access_token': ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"API error for media ID {media_id}: {e}")
            continue

        # Extract metrics
        metrics_data = {}
        if 'data' in data:
            for metric in data['data']:
                name = metric.get('name')
                if name and metric.get('values'):
                    metrics_data[name] = metric['values'][0].get('value', 0)

        video_views = metrics_data.get('views', 0)
        likes = metrics_data.get('likes', 0)
        comments = metrics_data.get('comments', 0)
        saves = metrics_data.get('saved', 0)  # API uses 'saved' for Saves column
        shares = metrics_data.get('shares', 0)

        # Calculate engagement rate
        total_engagement = likes + comments + saves + shares
        engagement_rate = (total_engagement / video_views * 100) if video_views > 0 else 0.0

        # Update row data (columns 3 to 8)
        row[3] = str(video_views)
        row[4] = str(likes)
        row[5] = str(comments)
        row[6] = str(saves)
        row[7] = str(shares)
        row[8] = f"{engagement_rate:.2f}%"

        print(f"Updated metrics for post ID: {media_id}")

    # Write updated data back to CSV
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("All posts updated successfully!")

if __name__ == "__main__":
    csv_file_path = "instagram_posts.csv"
    update_all_posts(csv_file_path)