import pandas as pd


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv("ml_dataset.csv")

# Make sure sentiment column exists
df["sentiment"] = df["sentiment"].fillna("")

# Only work with comments that are not labelled yet
unlabelled = df[df["sentiment"] == ""].copy()

# Make sure comment text is treated as text
unlabelled["comment_text"] = (
    unlabelled["comment_text"]
    .fillna("")
    .astype(str)
)


# --------------------------------------------------
# 2. Keywords / phrases
# --------------------------------------------------

negative_words = [
    # English
    "worst",
    "bad",
    "boring",
    "disappointed",
    "disappointing",
    "hate",
    "poor",
    "waste",
    "overacting",
    "over action",
    "not good",
    "not worth",
    "terrible",
    "cringe",
    "disaster",
    "flop",
    "average",
    "below average",
    "weak",
    "pathetic",
    "slow",
    "drag",
    "waste of",
    "dislike",

    # Malayalam
    "പോരാ",
    "മോശം",
    "ബോർ",
    "ബോറിംഗ്",
    "വേസ്റ്റ്",
    "അഭിനയം പോരാ",
    "ഓവർ ആക്ടിംഗ്",
    "ദുരന്തം",
    "പരാജയം"
]


neutral_words = [
    # English
    "when",
    "where",
    "what",
    "who",
    "how",
    "release",
    "release date",
    "ott",
    "collection",
    "budget",
    "runtime",
    "duration",
    "cast",
    "hero",
    "director",
    "producer",
    "theatre",
    "theater",
    "location",
    "available",

    # Malayalam
    "എപ്പോൾ",
    "എവിടെ",
    "എന്ത്",
    "ആരാണ്",
    "എങ്ങനെ",
    "റിലീസ്",
    "ഒടിടി",
    "കളക്ഷൻ",
    "ബഡ്ജറ്റ്",
    "ദൈർഘ്യം",
    "തിയേറ്റർ"
]


# --------------------------------------------------
# 3. Helper function
# --------------------------------------------------

def contains_word(text, words):
    text = text.lower()

    for word in words:
        if word.lower() in text:
            return True

    return False


# --------------------------------------------------
# 4. Find possible negative comments
# --------------------------------------------------

negative_candidates = unlabelled[
    unlabelled["comment_text"].apply(
        lambda x: contains_word(x, negative_words)
    )
].copy()


# --------------------------------------------------
# 5. Find possible neutral comments
# --------------------------------------------------

neutral_candidates = unlabelled[
    unlabelled["comment_text"].apply(
        lambda x: contains_word(x, neutral_words)
    )
].copy()


# --------------------------------------------------
# 6. Find random comments
# --------------------------------------------------
# These are important because we don't want the ML
# dataset to contain only keyword-based comments.

random_candidates = unlabelled.sample(
    n=min(100, len(unlabelled)),
    random_state=42
).copy()


# --------------------------------------------------
# 7. Remove duplicates
# --------------------------------------------------

negative_candidates = negative_candidates.drop_duplicates(
    subset=["comment_id"]
)

neutral_candidates = neutral_candidates.drop_duplicates(
    subset=["comment_id"]
)

random_candidates = random_candidates.drop_duplicates(
    subset=["comment_id"]
)


# --------------------------------------------------
# 8. Save separate files
# --------------------------------------------------

negative_candidates.to_csv(
    "negative_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)

neutral_candidates.to_csv(
    "neutral_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)

random_candidates.to_csv(
    "random_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# 9. Print results
# --------------------------------------------------

print("Candidate search completed!")

print()
print(f"Possible negative comments: {len(negative_candidates)}")
print(f"Possible neutral comments: {len(neutral_candidates)}")
print(f"Random comments for review: {len(random_candidates)}")

print()
print("Files created:")
print("negative_candidates.csv")
print("neutral_candidates.csv")
print("random_candidates.csv")

print()
print("IMPORTANT:")
print("These are ONLY candidate comments.")
print("Do NOT automatically assign the suggested sentiment.")
print("Review each comment manually before labelling.")