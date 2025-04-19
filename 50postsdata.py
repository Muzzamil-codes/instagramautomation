import requests
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
# Replace these with your own values:
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID")
MEDIA_LIMIT = 53  # Number of posts to fetch

# === FUNCTIONS ===

def get_all_posts(ig_account_id, access_token, limit=MEDIA_LIMIT):
    """
    Retrieve recent media objects from the Instagram Business Account.
    """
    url = f"https://graph.facebook.com/v22.0/{ig_account_id}/media"
    params = {
        'fields': 'id',
        'access_token': access_token,
        'limit': limit
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    if 'error' in data:
        print("Error fetching media:", data['error'])
        return []
    return data.get('data', [])

def get_media_insights(media_id, access_token, media_type):
    """
    Retrieve insights for a specific media object depending on media_type.
    """

    url = f"https://graph.facebook.com/v22.0/{media_id}/insights"
    params = {
        'metric': 'saved,views,likes,comments,shares',
        'access_token': access_token
    }

    response = requests.get(url, params=params)
    data = response.json()

    metrics_data = {}
    if 'data' in data:
        for metric in data['data']:
            if metric.get('values'):
                metrics_data[metric['name']] = metric['values'][0].get('value', 0)
    else:
        print(f"Warning: No insights data for media ID {media_id}. Response:", data)
    return metrics_data


def export_to_csv(posts, filename='instagram_posts.csv'):
    """
    For each post, fetch insights and calculate an engagement rate per view,
    then export the data sorted by engagement rate descending to a CSV file.
    """
    post_data = []
    
    for post in posts:
        media_id = post.get('id')
        params = {
            'access_token': ACCESS_TOKEN
        }
        response = requests.get(f"https://graph.facebook.com/v22.0/{media_id}?fields=permalink", params=params)
        link = response.json()
        link = link['permalink']
        # like_count = post.get('like_count', 0)
        # comments_count = post.get('comments_count', 0)
        
        # Fetch insights for this media item
        media_type = post.get('media_type', 'REEL')
        insights = get_media_insights(media_id, ACCESS_TOKEN, media_type)

        video_views = insights.get('views', 0)
        saved = insights.get('saved', 0)
        like_count = insights.get('likes', 0)
        comments_count = insights.get("comments", 0)
        shares = insights.get("shares", 0)

        # Calculate a simple engagement rate per view:
        total_engagement = like_count + comments_count + saved + shares
        if video_views > 0:
            engagement_rate_per_view = (total_engagement / video_views) * 100
        else:
            engagement_rate_per_view = 0  # Fallback for non-video posts
        
        post_data.append({
            'post_url': link,
            'post_id': media_id,
            'showerthought': '',
            'video_views': video_views,
            'like_count': like_count,
            'comments_count': comments_count,
            'saved': saved,
            'shares': shares,
            'engagement_rate_per_view': engagement_rate_per_view
        })

    # Sort posts by engagement rate descending
    sorted_posts = sorted(post_data, key=lambda x: x['engagement_rate_per_view'], reverse=True)
    

    with open(filename, 'r', newline='', encoding="utf-8") as file:
        rows = [row for row in csv.reader(file) if any(cell.strip() for cell in row)]

        for row in rows:
            for post in sorted_posts:
                if row[0] == post["post_url"]:
                    rows[rows.index(row)] = [
                    post['post_url'],
                    post['post_id'],
                    row[1],
                    post['video_views'],
                    post['like_count'],
                    post['comments_count'],
                    post['saved'],
                    post['shares'],
                    f"{post['engagement_rate_per_view']:.2f}%"
                    ]
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    # # Write to CSV
    # with open(filename, 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Post URL', 'Shower Thought', 'Video Views', 'Likes', 'Comments', 'Saves', 'shares', 'Engagement Rate'])
    #     for post in sorted_posts:
    #         writer.writerow([
    #             post['post_url'],
    #             post['showerthought'],
    #             post['video_views'],
    #             post['like_count'],
    #             post['comments_count'],
    #             post['saved'],
    #             post['shares'],
    #             f"{post['engagement_rate_per_view']:.2f}%"
    #         ])
    # print(f"Successfully exported {len(sorted_posts)} posts to '{filename}'")

def main():
    posts = get_all_posts(IG_BUSINESS_ACCOUNT_ID, ACCESS_TOKEN)
    if posts:
        export_to_csv(posts)
    else:
        print("Failed to retrieve posts.")

if __name__ == "__main__":
    main()
