📌 Project Overview
Dataset: YouTube Trending Videos - Kaggle
Tools: Python, Pandas, Power BI
Domain: Social Media Analytics

🔧 Data Cleaning (Python)
Steps performed in scripts/youtube_clean.py:

Fixed CSV parsing issues (40,949 rows recovered from broken 8k parse)
Converted dates from yy.dd.mm format to DD/MM/YYYY
Mapped category_id to category names using JSON file
Extracted tags from "tag1"|"tag2" format and counted them
Calculated derived metrics: engagement_rate, like_dislike_ratio, days_to_trend
Added views_bucket, trending_month, trending_year for Power BI slicers
Replaced all NaN and inf values with 0 for Power BI compatibility


📊 Dashboard Pages
Page 1 — Overview

KPI Cards: Total Videos, Avg Views, Avg Engagement Rate, Avg Days to Trend
Total Views by Category (bar chart)
Videos Trending by Month (line chart)
Videos by View Count Range (donut chart)
Slicers: Category, Year

Page 2 — Trending Analysis

Engagement vs Views by Category (scatter plot)
Top 10 Channels by Views (bar chart)
How Fast Do Videos Trend? (column chart)
Top Trending Videos (table)

Page 3 — Publish Patterns

Best Day to Publish (column chart)
Best Hour to Publish (column chart)
Tag Count vs Views (scatter plot)
Which Category Goes Viral Fastest? (bar chart)

Page 4 — Channel & Category

View Share by Category (treemap)
Most Trending Channels (bar chart)
Channel Category Mix (stacked bar)
Top Channel & Top Category (cards)


💡 Key Insights

🎵 Music & Entertainment dominate trending with the highest total views
📅 Tuesday and Wednesday videos get the highest average views
⚡ Nonprofits & Activism videos trend the fastest (avg ~5 days)
🎬 Film & Animation takes the longest to trend (avg ~37 days)
🏷️ Videos with 10–20 tags perform better than those with more or fewer
