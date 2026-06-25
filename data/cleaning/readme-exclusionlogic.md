# Service Article Filtering

## Overview

Before analysing education news, it was necessary to remove articles that primarily function as **service notifications** rather than substantive journalism.

Education sections of newspapers frequently contain articles such as:

* Examination results
* Admit card announcements
* Registration notices
* Merit lists
* Counselling schedules
* Recruitment notifications
* School assembly headlines

Although these articles are useful to readers, they do not represent policy discussions or broader public discourse. Including them would heavily skew the dataset towards examinations and administrative announcements.

This script applies a rule-based filtering approach to remove such articles while preserving news stories that discuss education policy, governance, reforms, institutional developments, or public issues.

---

## Classification Strategy

Each headline is assigned to one of three buckets:

| Bucket          | Description                                          |
| --------------- | ---------------------------------------------------- |
| **KEEP**        | Articles retained for downstream analysis.           |
| **AUTO_REMOVE** | Routine service notifications removed automatically. |
| **REVIEW**      | Borderline cases requiring manual inspection.        |

The classifier relies entirely on headline matching using curated keyword lists.

---

## Filtering Logic

The filtering pipeline follows the rules below:

1. **Always keep**

   * Government policies and reforms
   * Court cases and legal developments
   * Paper leak investigations
   * Institutional announcements
   * New academic programmes and courses
   * Research and international education stories
   * Student welfare and systemic education issues

2. **Automatically remove**

   * Examination results
   * Scorecards and marksheets
   * Admit cards and hall tickets
   * Registration and application notices
   * Counselling and seat allotments
   * Recruitment notifications
   * Topper interviews and preparation stories
   * School assembly news headlines

3. **Manual review**

   * Borderline administrative announcements that may contain broader policy relevance (for example, answer key articles).

---

## Output Files

Running the script produces three CSV files.

| File                       | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| `clean_articles.csv`       | Final corpus used for downstream analysis.              |
| `auto_remove_articles.csv` | Articles automatically excluded by the filtering rules. |
| `review_articles.csv`      | Borderline articles that require manual validation.     |

The script also prints a summary showing:

* Original dataset size
* Number of automatically removed articles
* Number of manually reviewed articles
* Final cleaned dataset size

---

## Why a Rule-Based Filter?

The objective of this stage is **high precision rather than high recall**.

Instead of attempting to classify every article using an LLM, the script removes highly repetitive service articles through deterministic rules and reserves ambiguous cases for manual review.

This approach offers three advantages:

* Transparent and reproducible filtering decisions.
* No dependence on external APIs or inference costs.
* Easy modification of keyword lists as new service article patterns emerge.

The final cleaned corpus forms the input for the subsequent theme, frame, and educational purpose analyses.
