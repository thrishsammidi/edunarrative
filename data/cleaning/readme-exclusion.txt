# Service Article Filtering

This script removes routine **service-oriented education articles** before downstream analysis.

Education news often contains administrative notifications such as examination results, admit cards, registrations, counselling schedules, recruitment notices, and school assembly headlines. 
While useful for readers, these articles do not contribute meaningfully to policy or discourse analysis and can disproportionately skew the dataset.

A rule-based keyword classifier categorises each article into one of three groups:

* **KEEP** – substantive education news retained for analysis.
* **AUTO_REMOVE** – routine service notifications removed automatically.
* **REVIEW** – borderline articles flagged for manual inspection.

The script outputs three files:

* `clean_articles.csv`
* `auto_remove_articles.csv`
* `review_articles.csv`

The filtering rules are fully configurable through keyword lists, making the process transparent, reproducible, and easy to adapt to future datasets.
