import argparse
from googleapiclient.discovery import build
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv("YOUTUBE_API_KEY")

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "malayalam_movie_analysis"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# COMMAND LINE ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser(
    description="Add a YouTube trailer and crawl its comments"
)

parser.add_argument(
    "--movie",
    required=True,
    help="Movie name already present in the database"
)

parser.add_argument(
    "--trailer",
    required=True,
    help="Name of the trailer"
)

parser.add_argument(
    "--video_id",
    required=True,
    help="YouTube video ID"
)

args = parser.parse_args()

movie_name = args.movie
trailer_name = args.trailer
video_id = args.video_id


# ============================================================
# YOUTUBE API
# ============================================================

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


print(f"\nFetching video data: {video_id}")


response = youtube.videos().list(
    part="snippet,statistics",
    id=video_id
).execute()


if not response["items"]:
    print("❌ YouTube video not found.")
    exit()


video = response["items"][0]

snippet = video["snippet"]
statistics = video["statistics"]


youtube_title = snippet["title"]
published_at = snippet["publishedAt"]

views = int(statistics.get("viewCount", 0))
likes = int(statistics.get("likeCount", 0))
comment_count = int(statistics.get("commentCount", 0))


# ============================================================
# DISPLAY VIDEO INFORMATION
# ============================================================

print("\nVideo information")
print("----------------------------")
print(f"Movie    : {movie_name}")
print(f"Trailer  : {trailer_name}")
print(f"Title    : {youtube_title}")
print(f"Views    : {views}")
print(f"Likes    : {likes}")
print(f"Comments : {comment_count}")
print("----------------------------")


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print("\nConnecting to PostgreSQL...")

connection = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)


with connection.cursor() as cursor:

    # ========================================================
    # FIND MOVIE
    # ========================================================

    cursor.execute(
        """
        SELECT movie_id
        FROM movies
        WHERE movie_name = %s;
        """,
        (movie_name,)
    )

    movie = cursor.fetchone()


    if not movie:
        print(f"\n❌ Movie '{movie_name}' does not exist.")
        print("Add the movie first using add_movie.py")
        connection.close()
        exit()


    movie_id = movie[0]

    print(f"\nMovie found.")
    print(f"Movie ID: {movie_id}")


    # ========================================================
    # CHECK WHETHER TRAILER ALREADY EXISTS
    # ========================================================

    cursor.execute(
        """
        SELECT trailer_id
        FROM trailers
        WHERE video_id = %s;
        """,
        (video_id,)
    )

    existing_trailer = cursor.fetchone()


    # ========================================================
    # UPDATE EXISTING TRAILER
    # ========================================================

    if existing_trailer:

        trailer_id = existing_trailer[0]

        print("\n🔄 Trailer already exists.")
        print("Updating YouTube statistics...")

        cursor.execute(
            """
            UPDATE trailers
            SET
                movie_id = %s,
                trailer = %s,
                youtube_title = %s,
                published_at = %s,
                views = %s,
                likes = %s,
                comment_count = %s
            WHERE trailer_id = %s;
            """,
            (
                movie_id,
                trailer_name,
                youtube_title,
                published_at,
                views,
                likes,
                comment_count,
                trailer_id
            )
        )

        print("✅ Trailer information updated.")


    # ========================================================
    # INSERT NEW TRAILER
    # ========================================================

    else:

        cursor.execute(
            """
            INSERT INTO trailers
            (
                movie_id,
                trailer,
                video_id,
                youtube_title,
                published_at,
                views,
                likes,
                comment_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING trailer_id;
            """,
            (
                movie_id,
                trailer_name,
                video_id,
                youtube_title,
                published_at,
                views,
                likes,
                comment_count
            )
        )

        trailer_id = cursor.fetchone()[0]

        print("\n🆕 New trailer added.")
        print(f"Trailer ID: {trailer_id}")


    # ========================================================
    # FETCH COMMENTS
    # ========================================================

    print("\nFetching comments...")

    next_page_token = None

    total_comments = 0
    new_comments = 0


    while True:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        )

        response = request.execute()


        # ====================================================
        # PROCESS COMMENTS
        # ====================================================

        for item in response["items"]:

            comment = item["snippet"]["topLevelComment"]

            youtube_comment_id = comment["id"]

            comment_data = comment["snippet"]

            author = comment_data["authorDisplayName"]

            comment_text = comment_data["textOriginal"]

            published = comment_data["publishedAt"]

            comment_likes = comment_data["likeCount"]


            total_comments += 1


            # =================================================
            # CHECK DUPLICATE
            # =================================================

            cursor.execute(
                """
                SELECT comment_id
                FROM comments
                WHERE youtube_comment_id = %s;
                """,
                (youtube_comment_id,)
            )

            existing_comment = cursor.fetchone()


            # =================================================
            # INSERT COMMENT
            # =================================================

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


        # ====================================================
        # NEXT PAGE
        # ====================================================

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break


# ============================================================
# SAVE
# ============================================================

connection.commit()

connection.close()


# ============================================================
# RESULT
# ============================================================

print("\nComment collection complete.")
print("----------------------------")
print(f"Comments found : {total_comments}")
print(f"New comments   : {new_comments}")
print("----------------------------")

print("\n✅ Trailer and comments successfully stored!")