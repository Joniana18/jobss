import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_jobs_from_pages(base_url, site_type, start_page=1):
    jobs = []
    page = start_page
    
    while True:
        if site_type == "duapune":
            url = f"{base_url}?page={page}"
        elif site_type == "punajuaj":
            url = f"{base_url}/page/{page}/"
        
        response = requests.get(url)
        if response.status_code != 200:
            break  # Stop if page request fails
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if site_type == "duapune":
            results = soup.find_all('div', class_='job-listing')
            for result in results:
                try:
                    job_title = result.find('h1', class_='job-title').find('a').text.strip()
                    company = result.find('small').find('a', style=True).text.strip()
                    location = result.find('span', class_='location').text.strip()
                    job_type = result.find('span', class_='time').text.strip()
                    expire = result.find('span', class_='expire').text.strip()
                    jobs.append([job_title, company, location, job_type, expire])
                except AttributeError:
                    continue

        elif site_type == "punajuaj":
            results = soup.find_all('div', class_='loop-item-content')
            for result in results:
                try:
                    job_title = result.find('h3', class_='loop-item-title').find('a').text.strip()
                    company = result.find('span', class_='job-company').text.strip() if result.find('span', class_='job-company') else 'No company found'
                    job_type = result.find('span', class_='job-type').text.strip() if result.find('span', class_='job-type') else 'No job type'
                    location = result.find('span', class_='job-location').text.strip() if result.find('span', class_='job-location') else 'No location found'
                    category = result.find('span', class_='job-category').text.strip() if result.find('span', class_='job-category') else 'No category'
                    language = result.find('span', class_='job-language').text.strip() if result.find('span', class_='job-language') else 'No language'
                    jobs.append([job_title, company, job_type, location, category, language])
                except AttributeError:
                    continue

        next_button = soup.find('a', class_='next page-numbers')
        if not next_button:
            break  # Stop if no "Next" button is found

        page += 1

    columns = ["Title", "Company", "Location", "Job Type", "Expire"] if site_type == "duapune" else ["Title", "Company", "Job Type", "Location", "Category", "Language"]
    return pd.DataFrame(jobs, columns=columns)

