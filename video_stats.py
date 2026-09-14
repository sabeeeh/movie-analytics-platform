from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = "9i5-s3jOwP8"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

request = youtube.videos().list(
    part="snippet,statistics",
    id=VIDEO_ID
)

response = request.execute()

video = response["items"][0]

print("Title:", video["snippet"]["title"])
print("Views:", video["statistics"]["viewCount"])
print("Likes:", video["statistics"]["likeCount"])
print("Comments:", video["statistics"]["commentCount"])