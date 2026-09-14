import pandas as pd

df = pd.read_csv("malayalam_trailer_comments.csv", encoding="utf-8-sig")

print("Number of comments:", len(df))
print("\nColumns:")
print(df.columns)

print("\nFirst 10 comments:")
print(df["text"].head(10).to_string())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate comments:")
print(df["text"].duplicated().sum())

print("\nEmpty comments:")
print((df["text"].str.strip() == "").sum())

print("\nDuplicate comments:")
print(df[df["text"].duplicated(keep=False)].sort_values("text")[["text"]].to_string(index=False))

print("\nLongest comments:")
print(df.loc[df["text"].str.len().sort_values(ascending=False).head(10).index, "text"].to_string(index=False))