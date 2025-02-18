import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_jobs_from_pages(base_url, site_type, start_page=1):
    # Initialize an empty list to store job details
    jobs = []
    page = start_page  # Set the starting page number
    
    while True:
        # Construct the URL for each page based on the site type
        if site_type == "duapune":
            url = f"{base_url}?page={page}"
        elif site_type == "punajuaj":
            url = f"{base_url}/page/{page}/"
        
        # Send an HTTP request to the constructed URL
        response = requests.get(url)
        
        # If the request fails (status code other than 200), break the loop
        if response.status_code != 200:
            break  # Stop if page request fails
        
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Scraping logic for the 'duapune' site
        if site_type == "duapune":
            # Find all job listings on the page
            results = soup.find_all('div', class_='job-listing')
            for result in results:
                try:
                    # Extract job details (title, company, location, job type, and expire date)
                    job_title = result.find('h1', class_='job-title').find('a').text.strip()
                    company = result.find('small').find('a', style=True).text.strip()
                    location = result.find('span', class_='location').text.strip()
                    job_type = result.find('span', class_='time').text.strip()
                    expire = result.find('span', class_='expire').text.strip()

                    # Append the job data to the jobs list
                    jobs.append([job_title, company, location, job_type, expire])
                except AttributeError:
                    # If any data is missing, skip this job
                    continue

        # Scraping logic for the 'punajuaj' site
        elif site_type == "punajuaj":
            # Find all job elements on the page
            results = soup.find_all('div', class_='loop-item-content')
            for result in results:
                try:
                    # Extract job details (title, company, job type, location, category, and language)
                    job_title = result.find('h3', class_='loop-item-title').find('a').text.strip()
                    company = result.find('span', class_='job-company').text.strip() if result.find('span', class_='job-company') else 'No company found'
                    job_type = result.find('span', class_='job-type').text.strip() if result.find('span', class_='job-type') else 'No job type'
                    location = result.find('span', class_='job-location').text.strip() if result.find('span', class_='job-location') else 'No location found'
                    category = result.find('span', class_='job-category').text.strip() if result.find('span', class_='job-category') else 'No category'
                    language = result.find('span', class_='job-language').text.strip() if result.find('span', class_='job-language') else 'No language'

                    # Append the job data to the jobs list
                    jobs.append([job_title, company, job_type, location, category, language])
                except AttributeError:
                    # If any data is missing, skip this job
                    continue

        # Check if there is a "Next" button to navigate to the next page
        next_button = soup.find('a', class_='next page-numbers')
        
        # If no "Next" button is found, stop the scraping process
        if not next_button:
            break  # Stop if no "Next" button is found

        # Increment the page number to scrape the next page
        page += 1

    # Define the columns for the DataFrame based on the site type
    if site_type == "duapune":
        columns = ["Title", "Company", "Location", "Job Type", "Expire"]
    elif site_type == "punajuaj":
        columns = ["Title", "Company", "Job Type", "Location", "Category", "Language"]
    
    # Return the jobs as a Pandas DataFrame
    return pd.DataFrame(jobs, columns=columns)

