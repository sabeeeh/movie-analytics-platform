import argparse
import psycopg


DB_NAME = "malayalam_movie_analysis"
DB_USER = "postgres"
DB_PASSWORD = "lolan123"
DB_HOST = "localhost"
DB_PORT = "5432"


parser = argparse.ArgumentParser(description="Add a movie to the database")

parser.add_argument(
    "--name",
    required=True,
    help="Movie name"
)

args = parser.parse_args()

movie_name = args.name


connection = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


with connection:
    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT movie_id
            FROM movies
            WHERE movie_name = %s;
            """,
            (movie_name,)
        )

        existing_movie = cursor.fetchone()

        if existing_movie:
            print(f"Movie already exists: {movie_name}")
            print(f"Movie ID: {existing_movie[0]}")

        else:
            cursor.execute(
                """
                INSERT INTO movies (movie_name, language)
                VALUES (%s, %s)
                RETURNING movie_id;
                """,
                (movie_name, "Malayalam")
            )

            movie_id = cursor.fetchone()[0]

            print(f"Movie added successfully: {movie_name}")
            print(f"Movie ID: {movie_id}")


connection.close()