import pandas as pd

# =========================
# LOAD DATA
# =========================

news = pd.read_csv("news_articles.csv")

# =========================
# TERMS
# =========================

# DEFINITELY REMOVE
AUTO_REMOVE_TERMS = [

    # Results
    "result",
    "results",
    "scorecard",
    "marksheet",
    "pass percentage",
    "pass rate",
    "toppers list",

    # Exam logistics
    "admit card",
    "hall ticket",
    "exam city slip",

    # Download/check articles
    "direct link",
    "how to check",
    "steps to check",
    "steps to download",
    "official website",
    "login credentials",
    "download scorecard",
    "download marksheet",

    # School assembly spam
    "school assembly",
    "school assembly news",
    "today news headlines",
    "news headlines for school assembly",
    "headlines for school assembly",
]

AUTO_REMOVE_TERMS.extend([
    "admission",
    "admissions",
    "registration",
    "registrations",
    "application",
    "applications",
    "counselling",
    "counseling",
    "merit list",
    "seat allotment",
    "allotment list",
    "recruitment",
    "vacancy",
    "correction window",
])

# Notification language
NOTIFICATION_TERMS = [
    "out",
    "released",
    "declared",
    "announced",
    "live updates",
    "check here",
    "check at",
    "websites to check",
]

# REVIEW MANUALLY
REVIEW_TERMS = [

    # Admissions
    "admission",
    "admissions",

    # Registration
    "registration",
    "registrations",

    # Applications
    "application",
    "applications",

    # Counselling
    "counselling",
    "counseling",

    # Merit lists
    "merit list",
    "seat allotment",
    "allotment list",

    # Recruitment
    "recruitment",
    "vacancy",
    "apply online",

    # Borderline
    "answer key",
]

# ALWAYS KEEP
KEEP_TERMS = [

    # Legal
    "court",
    "high court",
    "supreme court",
    "petition",
    "hearing",

    # Controversy
    "paper leak",
    "controversy",
    "investigation",
    "raises questions",
    "question raised",
    "criticism",
    "criticised",
    "alleges",
    "alleged",
    "irregularity",

    # Assessment issues
    "revaluation",
    "rechecking",

    # Policy
    "policy",
    "reform",
    "guidelines",
    "framework",
    "ministry",

    # Student issues
    "students demand",
    "student protest",
    "aspirants want",
    "mental health",

    # Education system
    "teacher shortage",
    "faculty shortage",
    "learning outcomes",
]

KEEP_TERMS.extend([
    "paper leak",
    "leak row",
    "new policy",
    "implements",
    "introduces",
    "launches",
    "new programme",
    "new program",
    "new course",
    "gate scores",
    "revaluation",
    "verification",
    "objection",
    "challenge",
    "relief",
])

KEEP_TERMS.extend([
    "introduces",
    "launches",
    "new programme",
    "new program",
    "new course",
    "scholarship",
    "internship",
    "research",
    "study abroad",
    "germany",
    "canada",
    "united states",
    "policy",
    "supreme court",
    "high court",
    "paper leak",
])

PROGRAM_KEEP_TERMS = [
    "launches",
    "launched",
    "introduces",
    "introduced",
    "new programme",
    "new program",
    "new course",
    "new courses",
    "new btech",
    "new degree",
    "curriculum",
    "study abroad",
    "germany",
    "united states",
    "us universities",
    "international students",
    "foreign universities",
]

ADMIN_TERMS = [
    "registration",
    "registrations",
    "application",
    "applications",
    "admission",
    "admissions",
    "counselling",
    "counseling",
    "merit list",
    "seat allotment",
    "recruitment",
    "vacancy",
    "answer key",
    "admit card",
    "correction window",
]

TOPPER_REMOVE_TERMS = [
    "topper",
    "toppers",
    "air 1",
    "all india rank 1",
    "rank holder",
    "shares preparation",
    "shares success",
    "preparation tips",
    "study routine",
    "crack neet",
    "crack jee",
]

# =========================
# CLASSIFIER
# =========================

def classify_article(headline):

    headline = str(headline).lower()

    # KEEP programme launches & international education stories
    if any(term in headline for term in PROGRAM_KEEP_TERMS):
        return "KEEP"

    # REMOVE topper stories
    if any(term in headline for term in TOPPER_REMOVE_TERMS):
        return "AUTO_REMOVE"
    
    # REMOVE topper stories
    if any(term in headline for term in ADMIN_TERMS):
        return "AUTO_REMOVE"

    # KEEP substantive stories
    if any(term in headline for term in KEEP_TERMS):
        return "KEEP"

    auto_score = sum(
        term in headline
        for term in AUTO_REMOVE_TERMS
    )

    notification_score = sum(
        term in headline
        for term in NOTIFICATION_TERMS
    )

    if auto_score >= 1 and notification_score >= 1:
        return "AUTO_REMOVE"

    if any(term in headline for term in REVIEW_TERMS):
        return "REVIEW"

    return "KEEP"

# =========================
# APPLY
# =========================

news["bucket"] = news["hl_title"].apply(
    classify_article
)

# =========================
# SPLIT FILES
# =========================

auto_remove = news[
    news["bucket"] == "AUTO_REMOVE"
].copy()

review = news[
    news["bucket"] == "REVIEW"
].copy()

clean = news[
    news["bucket"] == "KEEP"
].copy()

# =========================
# SAVE
# =========================

auto_remove.to_csv(
    "auto_remove_articles.csv",
    index=False
)

review.to_csv(
    "review_articles.csv",
    index=False
)

clean.to_csv(
    "clean_articles.csv",
    index=False
)

# =========================
# SUMMARY
# =========================

print("=" * 60)
print("ARTICLE FILTER SUMMARY")
print("=" * 60)

print(f"Original articles: {len(news):,}")
print(f"Auto remove: {len(auto_remove):,}")
print(f"Review manually: {len(review):,}")
print(f"Keep: {len(clean):,}")

print("\nSaved:")
print("auto_remove_articles.csv")
print("review_articles.csv")
print("clean_articles.csv")
