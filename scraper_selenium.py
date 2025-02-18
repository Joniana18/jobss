from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd

def scrape_all_jobs_selenium(base_url, site_type, start_page=1):
    options = webdriver.ChromeOptions()
    # Remove headless mode to see the browser
    # options.add_argument('--headless')  # Uncomment this line to run in headless mode

    # Use Service to avoid passing multiple values to WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    all_jobs = []

    try:
        if site_type == "duapune":
            driver.get(base_url)
            time.sleep(5)  # Allow time for the page to load

            # Click the "Kërko punë te tjera" link
            try:
                search_link = driver.find_element(By.CSS_SELECTOR, "a.all-listed-works")
                search_link.click()
                time.sleep(5)  # Allow time for the advanced search page to load
                print("Clicked 'Kërko punë te tjera' link")
            except Exception as e:
                print(f"Error clicking 'Kërko punë te tjera' link: {e}")
                return pd.DataFrame(all_jobs)

        page = start_page
        while True:
            if site_type == "duapune":
                url = f"https://duapune.com/search/advanced/filter?page={page}"
            elif site_type == "punajuaj":
                url = f"{base_url}/page/{page}/"
            
            driver.get(url)
            time.sleep(5)  # Increase time to allow full page load

            if site_type == "duapune":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-listing")
            elif site_type == "punajuaj":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.loop-item-content")

            print(f"Page {page}: Found {len(job_elements)} jobs")  # Debugging

            if not job_elements:
                print("No job elements found, stopping...")
                break  # Stop if no more jobs found

            for job_element in job_elements:
                try:
                    if site_type == "duapune":
                        title = job_element.find_element(By.CSS_SELECTOR, "h1.job-title a").text.strip()
                        company = job_element.find_element(By.CSS_SELECTOR, "small a[style]").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "small a[style]") else "No company found"
                        job_type = job_element.find_element(By.CSS_SELECTOR, "span.time").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.time") else "No job type"
                        location = job_element.find_element(By.CSS_SELECTOR, "span.location").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.location") else "No location found"
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

            # Check for the presence of a "Next" button
            if site_type == "duapune":
                next_button = driver.find_elements(By.CSS_SELECTOR, "a.relative.inline-flex.items-center.px-4.py-2.ml-3.text-sm.font-medium.text-gray-700.bg-white.border.border-gray-300.leading-5.rounded-md.hover:text-gray-500.focus:outline-none.focus:ring.ring-gray-300.focus:border-blue-300.active:bg-gray-100.active:text-gray-700.transition.ease-in-out.duration-150")
            elif site_type == "punajuaj":
                next_button = driver.find_elements(By.CSS_SELECTOR, "a.next.page-numbers")
                
            if not next_button:
                print("No next button found, stopping...")
                break  # Stop if no "Next" button is found

            page += 1
    
    finally:
        driver.quit()

    return pd.DataFrame(all_jobs)
