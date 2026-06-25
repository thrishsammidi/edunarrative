# edunarrative
A data-driven exploration of education priorities across government communications and news media.

ARTICLE: https://substack.com/home/post/p-203526156

## Overview

This project explores whether the Government of India and mainstream education news communicate education through similar narratives.

To investigate this, I collected:

* **238 Ministry of Education press releases** published through the Press Information Bureau (PIB)
* **~4,000 education articles** from *The Indian Express*

Rather than studying policy effectiveness, this project focuses on **policy communication**—asking whether government priorities and public discourse present education with the same underlying purpose.

---

## Methodology

The analysis consists of three stages.

### 1. Data Collection

Articles were scraped using **Scrapy and Selenium**.

Sources include:

* Ministry of Education press releases (PIB)
* Indian Express Education

---

### 2. Dataset Cleaning

Routine service articles were removed using a rule-based filtering pipeline.

Examples include:

* Examination results
* Admit cards
* Counselling notices
* Merit lists
* Recruitment notifications
* School assembly headlines

The aim was to retain substantive education reporting while removing administrative announcements that would otherwise dominate the corpus.

---

### 3. LLM-assisted Classification

Articles were classified using **OpenAI GPT-5 Mini** into three hierarchical dimensions.

## Themes

Themes describe **what the article is about.**

The following themes were designed for this project:

* Governance & Regulation
* Higher Education & Research
* Examinations & Admissions Governance
* Teacher Development & Quality
* Student Welfare & Well-being
* Curriculum & Pedagogy
* Equity, Access & Inclusion
* School Infrastructure & Operations
* Culture & Integration

These themes form the quantitative comparison between government and media attention.

---

## Frames

Frames describe **how education is presented.**

Each article is assigned one dominant frame.

* Institution Building
* Nation Building
* Innovation & Research
* Career Mobility
* Accountability & Oversight
* Student Experience

For example, two articles discussing higher education may belong to the same theme but frame education differently—one as institutional expansion, another as career opportunity.

---

## Educational Purpose

Purpose attempts to capture **why education is portrayed as important** within the article.

Each article is classified into one educational purpose.

* Human Capital Development
* National Integration
* Governance Reform
* Knowledge Creation
* Economic Mobility
* Social Welfare

This additional layer moves beyond topic modelling and attempts to capture the broader policy narrative communicated by each source.

---

## Findings

The project compares government communications and mainstream education news across three levels:

* Theme composition
* Communication frames
* Educational purpose

The objective is to understand how different actors communicate education, rather than evaluating whether those priorities are correct.

---


## Limitations

* News corpus is limited to *The Indian Express*.
* Theme, frame, and purpose definitions were designed specifically for this project.
* LLM classifications were manually reviewed on sampled outputs.
* The analysis focuses on communication narratives and should not be interpreted as an evaluation of policy effectiveness.

---

## Future Work

Potential extensions include:

* Expanding to additional news organisations.
* Human validation of LLM classifications.
* Longitudinal analysis of communication trends.
* Comparison with education budgets and policy outcomes.

Feedback and critiques are always welcome.
