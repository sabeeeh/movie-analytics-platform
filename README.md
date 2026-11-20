# Malayalam Movie Audience Analytics

An end-to-end data project that collects YouTube trailer data for Malayalam movies, stores it in PostgreSQL, and analyses how audiences react, including sentiment in Malayalam, Manglish and English comments.

> **Status:** In development. Data collection and storage are working. SQL analysis, the sentiment model and the dashboard are next.

---

## Why this project

Most trailer analysis covers Hollywood or Bollywood. Malayalam cinema has a large and very active online audience, but its comments are hard to analyse because people write in **Malayalam script, Manglish (Malayalam typed in English letters), English, or a mix of all three**, often with emojis and slang.

This project builds the full workflow, from raw API data to audience insights, and treats that language mix as a core part of the problem.

## What it does

- Collects trailer statistics from the **YouTube Data API**: views, likes, comment count and publish date
- Collects individual **comments** with their dates and like counts
- Stores everything in a relational **PostgreSQL** database (`movies → trailers → comments`)
- Updates trailer statistics on repeat runs **without creating duplicate records**
- Prepares comments for **sentiment classification** (positive / negative / neutral)

## Architecture

```text
YouTube Data API
       |
       v
Python collection scripts
       |
       v
PostgreSQL database
       |
       v
Cleaning and preparation
       |
       v
SQL + Pandas analysis
       |
       v
Sentiment model (TF-IDF + Logistic Regression)
       |
       v
Power BI dashboard
```

## Tech stack

| Area | Tools |
|---|---|
| Language | Python |
| Data source | YouTube Data API v3 |
| Database | PostgreSQL, psycopg |
| Data processing | Pandas |
| Machine learning | scikit-learn (planned) |
| Visualisation | Power BI (planned) |
| Version control | Git, GitHub |

## Database design

One movie can have many trailers, and one trailer can have many comments.

| Table | Purpose |
|---|---|
| `movies` | Movie name and language |
| `trailers` | One row per YouTube video, with its statistics |
| `comments` | One row per comment, linked to a trailer |

The `trailers` table keeps my own label (for example *Teaser*) separate from the original YouTube title, and `video_id` is unique so a trailer can never be added twice.

| Column | Description |
|---|---|
| `trailer_id` | Primary key |
| `movie_id` | Foreign key to `movies` |
| `video_id` | YouTube video ID (unique) |
| `trailer` | My own label, e.g. "Teaser Trailer" |
| `youtube_title` | Original title from YouTube |
| `published_at` | Publish date and time |
| `views`, `likes`, `comment_count` | Latest statistics |

## Example: tracking one trailer over time

The *Credit Score* teaser was tracked over several runs. Each run updates the same trailer row instead of adding a new one.

| Run | Views | Likes | Comments |
|---|---:|---:|---:|
| 1 | 1,300,706 | 3,967 | 289 |
| 2 | 1,310,216 | 3,978 | 291 |
| 3 | 1,330,327 | 4,013 | 339 |

## Project files

| File | What it does |
|---|---|
| `add_movie.py` | Adds a movie to the database (skips it if it already exists) |
| `add_trailer.py` | Adds a trailer, fetches its YouTube stats and collects its comments |
| `youtube_comments.py` | Retrieves comments from the YouTube API |
| `video_stats.py` | Retrieves video statistics |
| `youtube_to_database.py` | Saves YouTube data into PostgreSQL |
| `analyze_comments.py` | Basic analysis of collected comments |
| `prepare_ml_dataset.py` | Builds a comment sample for manual sentiment labelling |
| `scripts.py` | Utility scripts |

## Getting started

### 1. Requirements

- Python 3.12.4
- PostgreSQL installed and running locally
- A YouTube Data API key ([how to get one](https://developers.google.com/youtube/v3/getting-started))

### 2. Install

```bash
git clone https://github.com/sabeeeh/movie-analytics-platform.git
cd movie-analytics-platform
pip install psycopg[binary] python-dotenv pandas google-api-python-client
```

### 3. Add your secrets

Create a `.env` file in the project folder. It is already listed in `.gitignore`, so it is never uploaded.

```env
YOUTUBE_API_KEY=your_api_key
DB_PASSWORD=your_database_password
```

### 4. Create the database

Create a PostgreSQL database named `malayalam_movie_analysis` with the `movies`, `trailers` and `comments` tables described above.

### 5. Run

Add a movie, then add a trailer for it:

```bash
python add_movie.py --name="Movie Name"
python add_trailer.py --movie="Movie Name" --trailer="Teaser Trailer" --video_id="YOUTUBE_VIDEO_ID"
```

Running `add_trailer.py` again for the same video refreshes its statistics.

## Roadmap

- [x] YouTube API integration
- [x] PostgreSQL schema and data loading
- [x] Trailer statistics tracking without duplicates
- [x] Credentials moved to environment variables
- [ ] Comment cleaning (Malayalam, Manglish, English, emojis)
- [ ] SQL exploratory analysis
- [ ] Manually labelled sentiment dataset (about 1,000 balanced comments)
- [ ] Sentiment model: TF-IDF + Logistic Regression, with evaluation
- [ ] Power BI dashboard
- [ ] Findings section

## Design decisions

- **Simple model first.** I'm starting with TF-IDF and Logistic Regression instead of a large pre-trained model, so every step of the pipeline is understandable and explainable.
- **Hand-labelled training data.** Sentiment labels are assigned manually, so the model learns from checked examples.
- **No secrets in code.** API keys and database passwords are read from environment variables.

## Findings

*Coming soon, after the analysis and modelling stages.*

## Author

**Sabeeh Sharof Perincheeri**
Research Analyst | Python, SQL, Power BI
[GitHub](https://github.com/sabeeeh)
