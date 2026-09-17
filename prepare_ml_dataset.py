import psycopg
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="malayalam_movie_analysis",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
    
)

query = """
SELECT
    c.comment_id,
    m.movie_name,
    t.trailer,
    c.comment_text
FROM comments c
JOIN trailers t
    ON c.trailer_id = t.trailer_id
JOIN movies m
    ON t.movie_id = m.movie_id
ORDER BY RANDOM()
LIMIT 1000;
"""

df = pd.read_sql_query(query, conn)

conn.close()

# Add an empty column for manual sentiment labeling
df["sentiment"] = ""

# Save the dataset
df.to_csv("ml_dataset.csv", index=False, encoding="utf-8-sig")

print(f"Dataset created successfully!")
print(f"Comments selected: {len(df)}")
print("File saved as: ml_dataset.csv")