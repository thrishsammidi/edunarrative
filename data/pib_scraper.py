"""
PIB Education Scraper with Selenium
Handles date filtering to scrape multiple months of data
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time

class PIBEducationScraperSelenium:
    
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.base_url = 'https://www.pib.gov.in/allRel.aspx?reg=8&lang=1'
        self.all_policies = []
    
    def scrape_date(self, year=None, month=None):
        """
        Scrape PIB for specific date or all dates
        If year/month are None, scrapes ALL available data
        Ministry of Education only
        """
        try:
            # Load page
            self.driver.get(self.base_url)
            time.sleep(3)

          
            print("    Selecting Region: National...")
            try:
                region_dropdown = Select(self.driver.find_element(By.ID, 'Bar1_ddlregion'))
                region_dropdown.select_by_value('48')  # 48 = National
                print("    Selected: National")
                time.sleep(1)
            except Exception as e:
                print(f"   Could not select Region: {e}")
                print("    (Continuing - National may already be selected)")
                time.sleep(1)
            
            print("  Selecting Language: English...")
            try:
                region_dropdown = Select(self.driver.find_element(By.ID, 'Bar1_ddlLang'))
                region_dropdown.select_by_value('1')
                print(" Selected: English")
                time.sleep(1)
            except Exception as e:
                print(f" Could not select Language: {e}")
                print(" (Continuing - Hindi may already be selected)")
                time.sleep(1)

            # Select Ministry of Education (value=8)
            print("    Selecting Ministry: Education...")
            try:
                ministry_dropdown = Select(self.driver.find_element(By.ID, 'ContentPlaceHolder1_ddlMinistry'))
                ministry_dropdown.select_by_value('8')  # 8 = Ministry of Education
                print("   Selected: Ministry of Education")
                time.sleep(1)
            except Exception as e:
                print(f"    Could not select Ministry: {e}")
            
            # Select Day = All (0)
            day_dropdown = Select(self.driver.find_element(By.ID, 'ContentPlaceHolder1_ddlday'))
            day_dropdown.select_by_value('0')  # 0 = All days
            time.sleep(1)
            
            # Select month (if provided)
            month_dropdown = Select(self.driver.find_element(By.ID, 'ContentPlaceHolder1_ddlMonth'))
            if month:
                month_dropdown.select_by_value(str(month))
            time.sleep(1)
            
            # Select year (if provided)
            year_dropdown = Select(self.driver.find_element(By.ID, 'ContentPlaceHolder1_ddlYear'))
            if year:
                year_dropdown.select_by_value(str(year))
            time.sleep(2)  # Wait for page to update
            
            # Parse the page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            policies = self._parse_page(soup, year, month)
            
            if policies:
                date_str = f"{year}-{month:02d}" if year and month else "all dates"
                print(f"  {date_str}: Found {len(policies)} policies")
            else:
                date_str = f"{year}-{month:02d}" if year and month else "all dates"
                print(f"  {date_str}: No articles found")
            
            self.all_policies.extend(policies)
            
            return len(policies)
        
        except Exception as e:
            print(f"✗ Error scraping {year}-{month:02d}: {e}")
            return 0
    
    def scrape_article_content(self, article_url):
        """
        Scrape full content from individual article
        Extracts: ' '.join(//p//span/text())
        """
        try:
            self.driver.get(article_url)
            time.sleep(1)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract content using the xpath: //p//span/text()
            content_parts = []
            
            # Find all <p> tags
            paragraphs = soup.find_all('p')
            
            for p in paragraphs:
                # Find all <span> inside this <p>
                spans = p.find_all('span')
                for span in spans:
                    text = span.get_text(strip=True)
                    if text:
                        content_parts.append(text)
            
            # Join all content with space
            content = ' '.join(content_parts)
            return content
        
        except Exception as e:
            print(f"   Error fetching content: {e}")
            return ""
    
    def _parse_page(self, soup, year, month):
        """Parse BeautifulSoup object and extract policies"""
        policies = []
        
        # Find content area using the correct selector
        content_area = soup.find('div', class_='content-area')
        
        if not content_area:
            return policies
        
        # Find all list items under content-area (as shown by user: //div[@class='content-area']//li)
        article_items = content_area.find_all('li')
        
        for idx, item in enumerate(article_items):
            # Skip header items (those with h3)
            if item.find('h3'):
                continue
            
            # Find article link
            link = item.find('a', href=lambda x: x and '/PressReleasePage.aspx' in x)
            if not link:
                continue
            
            try:
                title = link.get('title', link.text.strip())
                href = link.get('href', '')
                full_url = f"https://www.pib.gov.in{href}" if href.startswith('/') else href
                prid = href.split('PRID=')[1].split('&')[0] if 'PRID=' in href else ''
                
                # Get date from span.publishdatesmall
                date_span = item.find('span', class_='publishdatesmall')
                date_str = date_span.text.replace('Posted On: ', '').strip() if date_span else 'Unknown'
                
                # Fetch full content from article link
                print(f"      Fetching content for: {title[:50]}...")
                article_content = self.scrape_article_content(full_url)
                
                policy = {
                    'title': title,
                    'prid': prid,
                    'url': full_url,
                    'announced_date': date_str,
                    'content': article_content,
                    'source': 'PIB',
                    'ministry': 'Ministry of Education'
                }
                
                policies.append(policy)
            
            except Exception as e:
                continue
        
        return policies
    
    def scrape_range(self, start_year, start_month, end_year, end_month):
        """Scrape date range, skipping empty months"""
        
        from datetime import date
        
        current = date(start_year, start_month, 1)
        end = date(end_year, end_month, 1)
        
        total = 0
        skipped = 0
        
        while current <= end:
            try:
                scraped = self.scrape_date(current.year, current.month)
                
                if scraped == 0:
                    print(f" Skipped {current.year}-{current.month:02d} (no articles)")
                    skipped += 1
                else:
                    total += scraped
                
                time.sleep(0.5)  # Short delay between requests
            
            except Exception as e:
                print(f"  Error on {current.year}-{current.month:02d}: {e}")
                skipped += 1
            
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        
        print(f"\n✓ Total policies: {total}")
        print(f"⊘ Skipped months: {skipped}")
        return total
    
    def scrape_past_12_months(self):
        """Scrape past 12 months, skipping empty months"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        year_ago = today - timedelta(days=365)
        
        print(f"Scraping {year_ago.year}-{year_ago.month:02d} to {today.year}-{today.month:02d}")
        print("(Skipping months with no articles)\n")
        
        return self.scrape_range(year_ago.year, year_ago.month, today.year, today.month)
    
    def get_dataframe(self):
        """Return DataFrame of all policies"""
        return pd.DataFrame(self.all_policies)
    
    def save_csv(self, filename='pib_education_policies_selenium.csv'):
        """Save to CSV"""
        df = self.get_dataframe()
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✓ Saved {len(df)} policies to {filename}")
        return df
    
    def close(self):
        """Close browser"""
        self.driver.quit()


# Usage
if __name__ == '__main__':
    print("PIB Education Policy Scraper (Selenium)")
    print("="*80)
    
    scraper = PIBEducationScraperSelenium(headless=False)  # Set to True for headless mode
    
    try:
        print("\nScraping Ministry of Education - Past 12 Months")
        print("(Will skip empty months and continue)\n")
        result = scraper.scrape_past_12_months()
        
        # Save to CSV
        df = scraper.save_csv()
        
        # Display summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total policies scraped: {len(df)}")
        
        if len(df) == 0:
            print("\n No policies were scraped!")
        else:
            print(f"Date range: {df['announced_date'].min()} to {df['announced_date'].max()}")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        scraper.close()
