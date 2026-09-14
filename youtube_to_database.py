import argparse
from googleapiclient.discovery import build
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================

API_KEY = os.getenv("YOUTUBE_API_KEY")

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "malayalam_movie_analysis"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==========================================
# COMMAND-LINE ARGUMENT
# ==========================================

parser = argparse.ArgumentParser(
    description="Fetch YouTube video data and comments."
)

parser.add_argument(
    "--video_id",
    required=True,
    help="YouTube video ID"
)

args = parser.parse_args()

VIDEO_ID = args.video_id


# ==========================================
# CONNECT TO YOUTUBE
# ==========================================

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


# ==========================================
# GET VIDEO INFORMATION
# ==========================================

print(f"\nFetching video data: {VIDEO_ID}")

response = youtube.videos().list(
    part="snippet,statistics",
    id=VIDEO_ID
).execute()


if not response["items"]:
    print("❌ Video not found.")
    exit()


video = response["items"][0]

snippet = video["snippet"]
statistics = video["statistics"]

title = snippet["title"]
published_at = snippet["publishedAt"]

views = int(statistics.get("viewCount", 0))
likes = int(statistics.get("likeCount", 0))
comment_count = int(statistics.get("commentCount", 0))


print("\nVideo information")
print("----------------------------")
print(f"Title    : {title}")
print(f"Views    : {views}")
print(f"Likes    : {likes}")
print(f"Comments : {comment_count}")
print("----------------------------")


# ==========================================
# CONNECT TO POSTGRESQL
# ==========================================

print("\nConnecting to PostgreSQL...")

connection = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)


# ==========================================
# DATABASE OPERATIONS
# ==========================================

with connection.cursor() as cursor:

    # --------------------------------------
    # CHECK IF TRAILER EXISTS
    # --------------------------------------

    cursor.execute(
        """
        SELECT trailer_id
        FROM trailers
        WHERE video_id = %s;
        """,
        (VIDEO_ID,)
    )

    existing_trailer = cursor.fetchone()


    # ======================================
    # EXISTING TRAILER → UPDATE
    # ======================================

    if existing_trailer:

        trailer_id = existing_trailer[0]

        cursor.execute(
            """
            UPDATE trailers
            SET
                title = %s,
                published_at = %s,
                views = %s,
                likes = %s,
                comment_count = %s
            WHERE video_id = %s;
            """,
            (
                title,
                published_at,
                views,
                likes,
                comment_count,
                VIDEO_ID
            )
        )

        print("\n🔄 Existing trailer found.")
        print("✅ Statistics updated.")


    # ======================================
    # NEW TRAILER → INSERT
    # ======================================

    else:

        cursor.execute(
            """
            INSERT INTO movies
            (
                movie_name,
                release_date,
                language
            )
            VALUES (%s, %s, %s)
            RETURNING movie_id;
            """,
            (
                title,
                published_at[:10],
                "Malayalam"
            )
        )

        movie_id = cursor.fetchone()[0]


        cursor.execute(
            """
            INSERT INTO trailers
            (
                movie_id,
                video_id,
                title,
                published_at,
                views,
                likes,
                comment_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING trailer_id;
            """,
            (
                movie_id,
                VIDEO_ID,
                title,
                published_at,
                views,
                likes,
                comment_count
            )
        )

        trailer_id = cursor.fetchone()[0]

        print("\n🆕 New trailer added.")


    # ======================================
    # FETCH COMMENTS
    # ======================================

    print("\nFetching comments...")

    next_page_token = None

    total_comments_found = 0
    new_comments = 0


    while True:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=VIDEO_ID,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        )

        response = request.execute()


        # ----------------------------------
        # PROCESS EACH COMMENT
        # ----------------------------------

        for item in response["items"]:

            comment = item["snippet"]["topLevelComment"]

            youtube_comment_id = comment["id"]

            comment_data = comment["snippet"]

            author = comment_data["authorDisplayName"]

            comment_text = comment_data["textOriginal"]

            published = comment_data["publishedAt"]

            comment_likes = comment_data["likeCount"]

            total_comments_found += 1


            # ------------------------------
            # CHECK EXISTING COMMENT
            # ------------------------------

            cursor.execute(
                """
                SELECT comment_id
                FROM comments
                WHERE youtube_comment_id = %s;
                """,
                (youtube_comment_id,)
            )

            existing_comment = cursor.fetchone()


            # ------------------------------
            # INSERT NEW COMMENT
            # ------------------------------

            if not existing_comment:

                cursor.execute(
                    """
                    INSERT INTO comments
                    (
                        trailer_id,
                        youtube_comment_id,
                        author,
                        comment_text,
                        published_at,
                        like_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        trailer_id,
                        youtube_comment_id,
                        author,
                        comment_text,
                        published,
                        comment_likes
                    )
                )

                new_comments += 1


        # ----------------------------------
        # NEXT PAGE
        # ----------------------------------

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break


# ==========================================
# SAVE EVERYTHING
# ==========================================

connection.commit()

connection.close()


# ==========================================
# RESULT
# ==========================================

print("\nComment collection complete.")
print("----------------------------")
print(f"Comments found : {total_comments_found}")
print(f"New comments   : {new_comments}")
print("----------------------------")

print("\n✅ Database update completed successfully!")