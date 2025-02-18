from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all_jobs_selenium(base_url, site_type, start_page=1):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    all_jobs = []

    try:
        if site_type == "duapune":
            driver.get(base_url)
            time.sleep(5)  

            # Try clicking the "Kërko punë te tjera" button
            try:
                search_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Kërko punë te tjera')]")
                driver.execute_script("arguments[0].click();", search_button)
                time.sleep(5)  
                print("Clicked 'Kërko punë te tjera' button")
            except Exception as e:
                print(f"Error clicking 'Kërko punë te tjera' button: {e}")
                return pd.DataFrame(all_jobs) 

        page = start_page
        while True:
            if site_type == "duapune":
                url = f"https://duapune.com/search/advanced/filter?page={page}"
            elif site_type == "punajuaj":
                url = f"{base_url}/page/{page}/"

            driver.get(url)
            time.sleep(5)  

            if site_type == "duapune":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-listing.col-md-12")
            elif site_type == "punajuaj":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.loop-item-content")

            print(f"Page {page}: Found {len(job_elements)} jobs") 

            if not job_elements:
                print("No job elements found, stopping...")
                break  

            for job_element in job_elements:
                try:
                    if site_type == "duapune":
                        title = job_element.find_element(By.CSS_SELECTOR, "h1.job-title a").text.strip()
                        company = job_element.find_element(By.CSS_SELECTOR, "small a").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "small a") else "No company found"
                        job_type = job_element.find_element(By.CSS_SELECTOR, "span.time").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.time") else "No job type"
                        location = job_element.find_element(By.CSS_SELECTOR, "div.job-details a").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "div.job-details a") else "No location found"
                        expire = job_element.find_element(By.CSS_SELECTOR, "span.expire").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.expire") else "No expire date"
                        
                        job_data = {
                            "Title": title,
                            "Company": company,
                            "Job Type": job_type,
                            "Location": location,
                            "Expire": expire
                        }
                    
                    elif site_type == "punajuaj":
                        title = job_element.find_element(By.CSS_SELECTOR, "h3.loop-item-title a").text.strip()
                        company = job_element.find_element(By.CSS_SELECTOR, "span.job-company").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-company") else "No company found"
                        job_type = job_element.find_element(By.CSS_SELECTOR, "span.job-type").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-type") else "No job type"
                        location = job_element.find_element(By.CSS_SELECTOR, "span.job-location").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-location") else "No location found"
                        category = job_element.find_element(By.CSS_SELECTOR, "span.job-category").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-category") else "No category"
                        language = job_element.find_element(By.CSS_SELECTOR, "span.job-language").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-language") else "No language"

                        job_data = {
                            "Title": title,
                            "Company": company,
                            "Job Type": job_type,
                            "Location": location,
                            "Category": category,
                            "Language": language
                        }

                    all_jobs.append(job_data)
                except Exception as e:
                    print(f"Error extracting job: {e}")
                    continue

            # Check for "Next" button
            if site_type == "duapune":
                next_button = driver.find_elements(By.XPATH, "//a[contains(text(), 'Vijuese »')]")
            elif site_type == "punajuaj":
                next_button = driver.find_elements(By.CSS_SELECTOR, "a.next.page-numbers")
                
            if not next_button:
                print("No next button found, stopping...")
                break  

            page += 1
    
    finally:
        driver.quit()

    return pd.DataFrame(all_jobs)
