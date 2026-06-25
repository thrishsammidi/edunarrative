import pandas as pd
import json
import os
from openai import OpenAI

# =====================================================
# CONFIG
# =====================================================

client = OpenAI(
    api_key=os.environ.get('api-key')
)

BATCH_SIZE = 5

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv("news_master.csv")

def safe_sample(df, theme, n):

    subset = df[df["theme"] == theme]

    print(f"{theme}: {len(subset)} rows")

    if len(subset) == 0:
        return pd.DataFrame()

    return subset.sample(
        min(n, len(subset)),
        random_state=42
    )

sample = pd.concat([

    safe_sample(
        df,
        "Examinations & Admissions Governance",
        75
    ),

    safe_sample(
        df,
        "Higher Education & Research",
        75
    ),

    safe_sample(
        df,
        "Governance & Regulation",
        75
    ),

    safe_sample(
        df,
        "Teacher Development & Quality",
        40
    ),

    safe_sample(
        df,
        "Student Welfare & Well-being",
        40
    )

], ignore_index=True)

sample = sample.reset_index(drop=True)

sample["row_id"] = sample.index

print(f"\nTotal sample size: {len(sample)}")

# =====================================================
# BATCH CLASSIFIER
# =====================================================

def classify_batch(batch):

    article_blocks = []

    for _, row in batch.iterrows():

        article_blocks.append(
f"""
ROW_ID: {row['row_id']}

TITLE:
{row['title']}

CONTENT:
{str(row['content'])[:500]}
"""
        )

    articles_text = "\n\n=========================\n\n".join(
        article_blocks
    )

    prompt = f"""
You are a public policy researcher.

For EACH article classify:

FRAME (choose exactly one)

- Institution Building
- Nation Building
- Innovation & Research
- Career Mobility
- Accountability & Oversight
- Student Experience

PURPOSE (choose exactly one)

- Human Capital Development
- National Integration
- Governance Reform
- Knowledge Creation
- Economic Mobility
- Social Welfare

Definitions:

Institution Building:
Administrative systems, governance, regulation, implementation, public institutions.

Nation Building:
National identity, citizenship, cultural integration, social cohesion.

Innovation & Research:
Research, science, technology, innovation ecosystems.

Career Mobility:
Admissions, placements, employability, scholarships, exams, career advancement.

Accountability & Oversight:
Court cases, grievances, controversies, investigations, failures.

Student Experience:
Mental health, wellbeing, inclusion, student life.

Human Capital Development:
Skill building, learning outcomes, capabilities.

National Integration:
Unity, cultural exchange, citizenship.

Governance Reform:
Administrative improvement, implementation, regulation.

Knowledge Creation:
Research, evidence generation, scientific discovery, data systems.

Economic Mobility:
Education as a pathway to jobs and advancement.

Social Welfare:
Wellbeing, inclusion, support systems.

Return ONLY valid JSON.

Format:

{{
  "results": [
    {{
      "row_id": 0,
      "frame": "Institution Building",
      "frame_confidence": 0.95,
      "purpose": "Governance Reform",
      "purpose_confidence": 0.90,
      "reasoning": "brief reason"
    }}
  ]
}}

ARTICLES:

{articles_text}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    text = response.choices[0].message.content

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)

# =====================================================
# RUN
# =====================================================

results = []

for start in range(
    0,
    len(sample),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(sample)
    )

    batch = sample.iloc[start:end]

    print(
        f"Processing rows {start} → {end}"
    )

    try:

        response = classify_batch(
            batch
        )

        results.extend(
            response["results"]
        )

    except Exception as e:

        print(
            f"FAILED BATCH {start}-{end}"
        )

        print(e)

# =====================================================
# RESULTS
# =====================================================

results_df = pd.DataFrame(results)

output = sample.merge(
    results_df,
    on="row_id",
    how="left"
)

# Convert confidence to %
for col in [
    "frame_confidence",
    "purpose_confidence"
]:

    if col in output.columns:

        output[col] = (
            output[col] * 100
        ).round(1)

output["min_conf"] = output[
    [
        "frame_confidence",
        "purpose_confidence"
    ]
].min(axis=1)

output = output.sort_values(
    "min_conf"
)

output.to_csv(
    "qualitative_news.csv",
    index=False
)

print(
    "\nSaved: qualitative_news.csv"
)

print(
    output[
        [
            "title",
            "theme",
            "frame",
            "frame_confidence",
            "purpose",
            "purpose_confidence"
        ]
    ].head(20)
)
