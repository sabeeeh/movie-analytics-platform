from googleapiclient.discovery import build
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Your YouTube API key
API_KEY = os.getenv("YOUTUBE_API_KEY")

# The YouTube video ID
VIDEO_ID = "9i5-s3jOwP8"

# Connect to YouTube
youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

comments = []

next_page_token = None

while True:

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=VIDEO_ID,
        maxResults=100,
        pageToken=next_page_token,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:

        comment = item["snippet"]["topLevelComment"]["snippet"]

        comments.append({
            "author": comment["authorDisplayName"],
            "published_at": comment["publishedAt"],
            "like_count": comment["likeCount"],
            "text": comment["textOriginal"]
        })

    next_page_token = response.get("nextPageToken")

    if not next_page_token:
        break

print("Total comments collected:", len(comments))

# Convert to a table
df = pd.DataFrame(comments)

# Save to CSV
df.to_csv("malayalam_trailer_comments.csv", index=False, encoding="utf-8-sig")

print("Saved to malayalam_trailer_comments.csv")