"""
EDUCATION POLICY & NEWS THEME CLASSIFIER - OPENAI VERSION
Version: Production (gpt-4o-mini)

Uses OpenAI API instead of Claude or Gemini
Classifies education articles into 8 themes based on:
- 2,675 news articles (clean_articles.csv)
- 232 policy documents (policies_cleaned.csv)

Themes optimized for semantic clarity and mutual exclusivity
"""

import pandas as pd
import json
from openai import OpenAI
import time
import os
from datetime import datetime

# Configure OpenAI API
API_KEY = os.environ.get("api-key")

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4o-mini"

# Final theme definitions with specific prompts
THEMES = {
    'Examinations & Admissions Governance': {
        'description': 'Exam administration, security, transparency, policy reforms. NOT result announcements.',
        'prompt': """This article discusses the GOVERNANCE, ADMINISTRATION, or POLICY of exams and admissions. Focus on: 
- Exam security, paper leaks, or transparency measures
- Changes to admission procedures or policies
- Evaluation system reforms
- Entrance exam policy changes (NEET/JEE/CBSE)
- Questions about fairness or credibility of exam systems
NOT about: Just announcing results, publishing answer keys, or listing cut-offs."""
    },
    
    'School Infrastructure & Operations': {
        'description': 'School buildings, facilities, closures, operational challenges.',
        'prompt': """This article discusses SCHOOL FACILITIES, INFRASTRUCTURE, or OPERATIONAL ISSUES.
Focus on:
- School closures (due to heatwave, pollution, emergencies)
- Classroom conditions (seating, ventilation, space)
- Physical facilities (labs, libraries, toilets, water)
- Safety infrastructure or facility problems
- Operational challenges (crowding, maintenance)"""
    },
    
    'Governance & Regulation': {
        'description': 'Education policy, regulations, implementation, government directives.',
        'prompt': """This article discusses EDUCATION POLICY, REGULATION, or GOVERNMENT DIRECTIVES.
Focus on:
- School fee regulation or fee policy changes
- Government policy implementation (NEP 2020, etc.)
- Regulatory frameworks and compliance
- School management guidelines
- Government education schemes and their rollout
- Cabinet decisions or Ministry directives affecting schools"""
    },
    
    'Higher Education & Research': {
        'description': 'Universities, colleges, research, higher education policy.',
        'prompt': """This article is about UNIVERSITIES, COLLEGES, or HIGHER EDUCATION INSTITUTIONS.
Focus on:
- University programs, convocations, or announcements
- IIT/AIIMS/NIT initiatives or developments
- Postgraduate programs or research initiatives
- University-level policy or academic standards
- Higher education rankings or institutional excellence
- Research funding or innovation at university level"""
    },
    
    'Curriculum & Pedagogy': {
        'description': 'Teaching methods, curriculum design, learning approaches.',
        'prompt': """This article is about HOW STUDENTS ARE TAUGHT or WHAT THEY LEARN.
Focus on:
- Curriculum design or curriculum changes
- Teaching methodology or pedagogical approaches
- Learning outcomes or assessment methods
- Subject-specific teaching (STEM, languages, etc.)
- Exam difficulty in relation to curriculum content
- New educational approaches (project-based, experiential, etc.)"""
    },
    
    'Equity, Access & Inclusion': {
        'description': 'Equal access, scholarships, rural education, marginalized groups.',
        'prompt': """This article is about EQUAL OPPORTUNITY or ACCESS for marginalized groups.
Focus on:
- Scholarship schemes or financial support programs
- Girl child education initiatives
- Rural or remote education programs
- SC/ST/OBC support or reservation-related education
- Support for disabled or special needs students
- Programs targeting low-income or marginalized communities"""
    },
    
    'Teacher Development & Quality': {
        'description': 'Teacher training, recruitment, qualifications, professional development.',
        'prompt': """This article is about TEACHERS: their training, quality, recruitment, or welfare.
Focus on:
- Teacher training or professional development programs
- Teacher recruitment or qualification standards
- Teacher salaries, working conditions, or welfare
- Teacher competency or quality improvement
- Teacher shortage or availability
- Teacher capacity building initiatives"""
    },
    
    'Student Welfare & Well-being': {
        'description': 'Student health, safety, mental health, counselling, well-being.',
        'prompt': """This article is about STUDENT HEALTH, SAFETY, or WELL-BEING.
Focus on:
- Mental health or counselling services for students
- Student safety or security initiatives
- Nutrition or health programs
- Stress, pressure, or well-being related to studies
- Anti-bullying or harassment prevention
- Student accommodation or hostel facilities"""
    }
}

def create_classification_prompt(headline, content_preview):
    """Create the classification prompt with all theme instructions"""
    
    prompt = f"""You are an expert in Indian education policy and media analysis.

CLASSIFY THIS ARTICLE INTO ONE EDUCATION THEME:

ARTICLE HEADLINE: {headline}

ARTICLE CONTENT (Preview): {content_preview[:1000]}

═══════════════════════════════════════════════════════════════════════════════

THEME OPTIONS:

1. Examinations & Admissions Governance
This article discusses the GOVERNANCE, ADMINISTRATION, or POLICY of exams and admissions. Focus on: 
- Exam security, paper leaks, or transparency measures
- Changes to admission procedures or policies
- Evaluation system reforms
- Entrance exam policy changes (NEET/JEE/CBSE)
- Questions about fairness or credibility of exam systems
NOT about: Just announcing results, publishing answer keys, or listing cut-offs.

2. School Infrastructure & Operations
This article discusses SCHOOL FACILITIES, INFRASTRUCTURE, or OPERATIONAL ISSUES.
Focus on:
- School closures (due to heatwave, pollution, emergencies)
- Classroom conditions (seating, ventilation, space)
- Physical facilities (labs, libraries, toilets, water)
- Safety infrastructure or facility problems
- Operational challenges (crowding, maintenance)

3. Governance & Regulation
This article discusses EDUCATION POLICY, REGULATION, or GOVERNMENT DIRECTIVES.
Focus on:
- School fee regulation or fee policy changes
- Government policy implementation (NEP 2020, etc.)
- Regulatory frameworks and compliance
- School management guidelines
- Government education schemes and their rollout
- Cabinet decisions or Ministry directives affecting schools

4. Higher Education & Research
This article is about UNIVERSITIES, COLLEGES, or HIGHER EDUCATION INSTITUTIONS.
Focus on:
- University programs, convocations, or announcements
- IIT/AIIMS/NIT initiatives or developments
- Postgraduate programs or research initiatives
- University-level policy or academic standards
- Higher education rankings or institutional excellence
- Research funding or innovation at university level

5. Curriculum & Pedagogy
This article is about HOW STUDENTS ARE TAUGHT or WHAT THEY LEARN.
Focus on:
- Curriculum design or curriculum changes
- Teaching methodology or pedagogical approaches
- Learning outcomes or assessment methods
- Subject-specific teaching (STEM, languages, etc.)
- Exam difficulty in relation to curriculum content
- New educational approaches (project-based, experiential, etc.)

6. Equity, Access & Inclusion
This article is about EQUAL OPPORTUNITY or ACCESS for marginalized groups.
Focus on:
- Scholarship schemes or financial support programs
- Girl child education initiatives
- Rural or remote education programs
- SC/ST/OBC support or reservation-related education
- Support for disabled or special needs students
- Programs targeting low-income or marginalized communities

7. Teacher Development & Quality
This article is about TEACHERS: their training, quality, recruitment, or welfare.
Focus on:
- Teacher training or professional development programs
- Teacher recruitment or qualification standards
- Teacher salaries, working conditions, or welfare
- Teacher competency or quality improvement
- Teacher shortage or availability
- Teacher capacity building initiatives

8. Student Welfare & Well-being
This article is about STUDENT HEALTH, SAFETY, or WELL-BEING.
Focus on:
- Mental health or counselling services for students
- Student safety or security initiatives
- Nutrition or health programs
- Stress, pressure, or well-being related to studies
- Anti-bullying or harassment prevention
- Student accommodation or hostel facilities

═══════════════════════════════════════════════════════════════════════════════

IMPORTANT RULES:
1. Pick the BEST MATCH (not multiple themes)
2. If article doesn't clearly fit any theme, respond with "Other"
3. Be specific about which theme and WHY

RETURN ONLY in this format:
THEME: [exact theme name from list above OR "Other"]
CONFIDENCE: [1-100 score, where 90-100=very confident, 70-89=confident, 50-69=uncertain, <50=low]
REASON: [1-2 sentences explaining your choice]

Do not include any other text. Just the three lines above."""
    
    return prompt

def classify_article(headline, content):
    """Classify a single article using OpenAI"""
    
    prompt = create_classification_prompt(headline, content)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for consistency
            max_tokens=200
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse response
        lines = response_text.split('\n')
        
        # Extract theme, confidence, reason
        theme = 'Unknown'
        confidence = 'Unknown'
        reason = ''
        
        for line in lines:
            if line.startswith('THEME:'):
                theme = line.replace('THEME:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                confidence = line.replace('CONFIDENCE:', '').strip()
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        classification = {
            'theme': theme,
            'confidence': confidence,
            'reason': reason
        }
        
        return classification
    
    except Exception as e:
        print(f" Error classifying: {e}")
        return {
            'theme': 'Error',
            'confidence': 'N/A',
            'reason': str(e)
        }

def classify_batch(csv_file, output_file='classified_output.csv', 
                   batch_size=None, start_idx=0, article_type='articles'):
    """Classify all items in a CSV file using OpenAI"""
    
    print("\n" + "="*80)
    print("THEME CLASSIFICATION - OPENAI VERSION")
    print(f"Model: {MODEL}")
    print("="*80)
    
    # Load data
    df = pd.read_csv(csv_file)
    total_items = len(df)
    
    # Filter if batch size specified
    if batch_size:
        df = df[start_idx:start_idx+batch_size]
    
    print(f"\n Processing {len(df)} {article_type}")
    print(f"   Total available: {total_items}")
    print(f"   Themes: {len(THEMES)}")
    print(f"   Output: {output_file}")
    print(f"   Model: {MODEL}")
    print(f"   Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get headline/title column name
    title_col = 'title'
    content_col = 'content'
    
    # Classification results
    results = []
    
    # Process items
    print(f"\n Starting classification...\n")
    start_time = time.time()
    
    for idx, row in df.iterrows():
        item_num = idx + 1
        
        # Show progress every 50 items
        if item_num % 50 == 0 or item_num == 1:
            elapsed = (time.time() - start_time) / 60
            if item_num > 1:
                rate = item_num / elapsed  # items per minute
                remaining_items = len(df) - item_num
                remaining_time = remaining_items / rate if rate > 0 else 0
                print(f"[{item_num:4d}/{len(df)}] {row[title_col][:60]:60s} | "
                      f"~{remaining_time:.0f}min remaining")
            else:
                print(f"[{item_num:4d}/{len(df)}] {row[title_col][:60]:60s}")
        
        # Classify
        classification = classify_article(
            row[title_col],
            row[content_col]
        )
        
        # Store result
        result = {
            'item_idx': idx,
            'headline': row[title_col],
            'theme': classification['theme'],
            'confidence': classification['confidence'],
            'reason': classification['reason']
        }
        
        # Add date if available
        if 'published_date' in row:
            result['date'] = row['published_date']
        elif 'announced_date' in row:
            result['date'] = row['announced_date']
        
        results.append(result)
        time.sleep(1.0)
    
    # Create dataframe
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv(output_file, index=False)
    
    # Show summary
    print("\n" + "="*80)
    print("CLASSIFICATION SUMMARY")
    print("="*80)
    
    theme_distribution = results_df['theme'].value_counts()
    print(f"\n Theme distribution ({len(results_df)} items):")
    print("-" * 80)
    
    for theme, count in theme_distribution.items():
        pct = (count / len(results_df)) * 100
        bar = "█" * int(pct/2)
        print(f"  {theme:40s} {count:4d} ({pct:5.1f}%) {bar}")
    
    # Confidence distribution
    print(f"\n🎯 Confidence distribution:")
    print("-" * 80)
    confidence_dist = results_df['confidence'].value_counts()
    for conf, count in confidence_dist.items():
        pct = (count / len(results_df)) * 100
        print(f"  {conf:10s}: {count:4d} ({pct:5.1f}%)")
    
    elapsed = (time.time() - start_time) / 60
    print(f"\n Total time: {elapsed:.1f} minutes")
    print(f" End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results_df

def show_sample(csv_file, n_samples=10):
    """Show sample classifications for manual review"""
    
    df = pd.read_csv(csv_file)
    sample = df.sample(n=min(n_samples, len(df)))
    
    print(f"\n\n{'='*80}")
    print(f"SAMPLE CLASSIFICATIONS ({len(sample)} articles)")
    print(f"{'='*80}\n")
    
    for idx, (_, row) in enumerate(sample.iterrows(), 1):
        print(f"{idx}. Headline: {row['headline'][:80]}")
        print(f"   Theme: {row['theme']}")
        print(f"   Confidence: {row['confidence']}")
        print(f"   Reason: {row['reason']}")
        print()

# ============================================================================
# USAGE
# ============================================================================

if __name__ == '__main__':
    
    import sys
    
    # OPTION 1: Classify news articles
    print("\n" + "="*80)
    print("READY TO CLASSIFY ARTICLES AND POLICIES (OPENAI)")
    print("="*80)
    
    print("\nOPTION 1: Test on 10 news articles")
    print("  python3 classify_themes_openai.py news-test")
    
    print("\nOPTION 2: Classify all news articles")
    print("  python3 classify_themes_openai.py news-all")
    
    print("\nOPTION 3: Test on 10 policies")
    print("  python3 classify_themes_openai.py policy-test")
    
    print("\nOPTION 4: Classify all policies")
    print("  python3 classify_themes_openai.py policy-all")
    
    print("\n" + "="*80)
    print("SETUP REQUIRED:")
    print("="*80)
    print("\n1. Get API key from: https://platform.openai.com/account/api-keys")
    print("2. Set environment: export OPENAI_API_KEY='sk-...'")
    print("3. Run test command above\n")
    
    # Default: test on news
    if len(sys.argv) < 2 or sys.argv[1] == 'news-test':
        print("\n→ Running: News articles test (10 samples)")
        results = classify_batch(
            'clean_articles.csv',
            output_file='news_classified_sample_openai.csv',
            batch_size=10,
            article_type='news articles'
        )
        show_sample('news_classified_sample_openai.csv', n_samples=10)
    
    elif sys.argv[1] == 'news-all':
        print("\n→ Running: All news articles")
        results = classify_batch(
            'clean_articles.csv',
            output_file='news_classified_all_openai.csv',
            article_type='news articles'
        )
    
    elif sys.argv[1] == 'policy-test':
        print("\n→ Running: Policies test (10 samples)")
        results = classify_batch(
            'policies_cleaned.csv',
            output_file='policies_classified_sample_openai.csv',
            batch_size=10,
            article_type='policies'
        )
        show_sample('policies_classified_sample_openai.csv', n_samples=10)
    
    elif sys.argv[1] == 'policy-all':
        print("\n→ Running: All policies")
        results = classify_batch(
            'policies_cleaned.csv',
            output_file='policies_classified_all_openai.csv',
            article_type='policies'
        )
