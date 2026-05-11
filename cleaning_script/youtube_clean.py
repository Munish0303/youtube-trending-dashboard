import pandas as pd
import json
import re

CSV_FILE  = "USvideos.csv"
JSON_FILE = "US_category_id.json"
OUTPUT    = "youtube_cleaned.csv"

# ─────────────────────────────────────────────────────────────
# 1. LOAD — 40k rows, proper quoting
# ─────────────────────────────────────────────────────────────
print("Loading CSV...")
df = pd.read_csv(
    CSV_FILE,
    encoding="latin1",
    engine="c",
    quotechar='"',
    doublequote=False,
    escapechar="\\",
    on_bad_lines="skip"
)
print(f"  Rows: {df.shape[0]}  Cols: {df.shape[1]}")

# ─────────────────────────────────────────────────────────────
# 2. DATES → dd.mm.yy
# trending_date raw: "17.14.11" = yy.dd.mm
# publish_time raw:  ISO 8601 with timezone
# ─────────────────────────────────────────────────────────────
print("\nFixing dates...")
df["trending_date"] = (
    pd.to_datetime(df["trending_date"], format="%y.%d.%m", errors="coerce")
    .dt.strftime("%d.%m.%y")
)

pub = pd.to_datetime(df["publish_time"], errors="coerce", utc=True)
df["publish_date"]    = pub.dt.strftime("%d.%m.%y")
df["publish_hour"]    = pub.dt.hour
df["publish_weekday"] = pub.dt.day_name()
df.drop(columns=["publish_time"], inplace=True)

print(f"  trending_date sample : {df['trending_date'].head(3).tolist()}")
print(f"  publish_date sample  : {df['publish_date'].head(3).tolist()}")

# ─────────────────────────────────────────────────────────────
# 3. CATEGORY NAME from JSON
# category_id in CSV is an integer, JSON keys are strings e.g. "22"
# ─────────────────────────────────────────────────────────────
print("\nMapping categories...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    cat_data = json.load(f)

cat_map = {item["id"]: item["snippet"]["title"] for item in cat_data["items"]}
# category_id loaded as int → convert to str to match JSON keys
df["category_name"] = df["category_id"].astype(str).map(cat_map).fillna("Unknown")

print(f"  Unique categories : {df['category_name'].nunique()}")
print(f"  Unknown rows      : {(df['category_name'] == 'Unknown').sum()}")

# ─────────────────────────────────────────────────────────────
# 4. TAGS — format: "tag1"|"tag2"|"tag3"
# Extract individual tags (strip quotes) and count them
# ─────────────────────────────────────────────────────────────
print("\nProcessing tags...")

def process_tags(raw):
    s = str(raw).strip()
    if s in ["[none]", "", "nan"]:
        return "", 0
    # extract all content inside double quotes
    tags = re.findall(r'"([^"]+)"', s)
    if not tags:
        # no quotes — split by | directly
        tags = [t.strip() for t in s.split("|") if t.strip()]
    return " | ".join(tags), len(tags)

df[["tags_clean", "tag_count"]] = df["tags"].apply(
    lambda x: pd.Series(process_tags(x))
)
df.drop(columns=["tags"], inplace=True)

print(f"  Avg tags per video : {df['tag_count'].mean():.1f}")
print(f"  Max tags           : {df['tag_count'].max()}")
print(f"  Sample             : {df['tags_clean'].iloc[1][:80]}")

# ─────────────────────────────────────────────────────────────
# 5. NUMERICS
# ─────────────────────────────────────────────────────────────
print("\nCleaning numerics...")
for col in ["views", "likes", "dislikes", "comment_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

# ─────────────────────────────────────────────────────────────
# 6. DERIVED METRICS
# ─────────────────────────────────────────────────────────────
print("\nCalculating metrics...")
views_f    = df["views"].astype("float64").replace(0, float("nan"))
dislikes_f = df["dislikes"].astype("float64").replace(0, float("nan"))

df["engagement_rate"]    = ((df["likes"].astype("float64") + df["comment_count"].astype("float64")) / views_f).round(4)
df["like_dislike_ratio"] = (df["likes"].astype("float64") / dislikes_f).round(2)

# ─────────────────────────────────────────────────────────────
# 7. FLAGS → 0 / 1
# ─────────────────────────────────────────────────────────────
for col in ["comments_disabled", "ratings_disabled", "video_error_or_removed"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper().map({"TRUE": 1, "FALSE": 0}).fillna(0).astype(int)

# ─────────────────────────────────────────────────────────────
# 8. REORDER COLUMNS
# ─────────────────────────────────────────────────────────────
ordered = [
    "video_id", "title", "channel_title",
    "category_id", "category_name",
    "trending_date", "publish_date", "publish_hour", "publish_weekday",
    "views", "likes", "dislikes", "comment_count",
    "engagement_rate", "like_dislike_ratio",
    "tags_clean", "tag_count",
    "thumbnail_link",
    "comments_disabled", "ratings_disabled", "video_error_or_removed",
    "description"
]
df = df[[c for c in ordered if c in df.columns]]

# ─────────────────────────────────────────────────────────────
# 9. SAVE
# ─────────────────────────────────────────────────────────────
df.to_csv(OUTPUT, index=False, encoding="utf-8")
print(f"\n✅ Done!  Rows: {df.shape[0]}  Cols: {df.shape[1]}  →  {OUTPUT}")
print("\nFinal columns:")
for c in df.columns:
    print(f"  {c} ({df[c].dtype})")
print("\nSample:")
print(df[["title","category_name","trending_date","publish_date","tag_count","engagement_rate"]].head(3).to_string())
