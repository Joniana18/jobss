from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all_jobs_selenium(base_url, site_type, start_page=1):
    # Initialize ChromeOptions for the browser (can add additional configurations here)
    options = webdriver.ChromeOptions()
    # Uncomment this line for headless mode (runs without opening a browser window)
    # options.add_argument('--headless')  
    
    # Set up ChromeDriver service using webdriver_manager to automatically manage the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # List to store all the jobs scraped
    all_jobs = []

    try:
        # Handle the case for specific sites like "duapune"
        if site_type == "duapune":
            driver.get(base_url)  # Navigate to the base URL
            time.sleep(5)  # Wait for the page to load (you can adjust the wait time based on page load speed)

            print("Checking initial page load...")
            # Print the first 1000 characters of the page source for debugging (to check if the page loaded properly)
            print(driver.page_source[:1000])  

            # Try to click the "Kërko punë te tjera" button to load more jobs
            try:
                search_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Kërko punë te tjera')]")
                ActionChains(driver).move_to_element(search_button).click().perform()  # Click the button
                time.sleep(5)  # Wait for the next page of jobs to load
                print("Clicked 'Kërko punë te tjera' button")
            except Exception as e:
                # If the button is not found or any other error occurs, print the error and return an empty DataFrame
                print(f"Error clicking 'Kërko punë te tjera' button: {e}")
                return pd.DataFrame(all_jobs) 

        # Start the scraping from the specified start page
        page = start_page
        while True:
            # Set the correct URL for each site depending on the page number
            if site_type == "duapune":
                url = f"https://duapune.com/search/advanced/filter?page={page}"
            elif site_type == "punajuaj":
                url = f"{base_url}/page/{page}/"

            # Load the URL for the current page
            driver.get(url)
            time.sleep(5)  # Wait for the page to load

            # Scroll down to ensure that all JavaScript-loaded jobs are rendered
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait after scrolling for new jobs to load

            print(f"Loaded page: {url}")
            # Print the first 1000 characters of the page source for debugging
            print(driver.page_source[:1000])  

            # Select job elements depending on the site type
            if site_type == "duapune":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-listing")
            elif site_type == "punajuaj":
                job_elements = driver.find_elements(By.CSS_SELECTOR, "div.loop-item-content")

            # Debugging: Print number of job elements found on the page
            print(f"Page {page}: Found {len(job_elements)} jobs") 

            # Stop scraping if no job elements are found (e.g., last page)
            if not job_elements:
                print("No job elements found, stopping...")
                break  

            # Loop through each job element and extract job details
            for job_element in job_elements:
                try:
                    # Extract job details for 'duapune' site
                    if site_type == "duapune":
                        title = job_element.find_element(By.CSS_SELECTOR, "h1.job-title a").text.strip()
                        company = job_element.find_element(By.CSS_SELECTOR, "small a").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "small a") else "No company found"
                        job_type = job_element.find_element(By.CSS_SELECTOR, "span.time").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.time") else "No job type"
                        location = job_element.find_element(By.CSS_SELECTOR, "div.job-details a").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "div.job-details a") else "No location found"
                        expire = job_element.find_element(By.CSS_SELECTOR, "span.expire").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.expire") else "No expire date"

                        # Create a dictionary to store job data
                        job_data = {
                            "Title": title,
                            "Company": company,
                            "Job Type": job_type,
                            "Location": location,
                            "Expire": expire
                        }

                    # Extract job details for 'punajuaj' site
                    elif site_type == "punajuaj":
                        title = job_element.find_element(By.CSS_SELECTOR, "h3.loop-item-title a").text.strip()
                        company = job_element.find_element(By.CSS_SELECTOR, "span.job-company").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-company") else "No company found"
                        job_type = job_element.find_element(By.CSS_SELECTOR, "span.job-type").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-type") else "No job type"
                        location = job_element.find_element(By.CSS_SELECTOR, "span.job-location").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-location") else "No location found"
                        category = job_element.find_element(By.CSS_SELECTOR, "span.job-category").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-category") else "No category"
                        language = job_element.find_element(By.CSS_SELECTOR, "span.job-language").text.strip() if job_element.find_elements(By.CSS_SELECTOR, "span.job-language") else "No language"

                        # Create a dictionary to store job data
                        job_data = {
                            "Title": title,
                            "Company": company,
                            "Job Type": job_type,
                            "Location": location,
                            "Category": category,
                            "Language": language
                        }

                    # Append the job data to the list
                    all_jobs.append(job_data)
                except Exception as e:
                    # If an error occurs while extracting a job, print the error and continue to the next job
                    print(f"Error extracting job: {e}")
                    continue  # Continue to the next job if there's an error with this one

            # Check if the "Next" button exists to navigate to the next page
            if site_type == "duapune":
                next_button = driver.find_elements(By.XPATH, "//a[contains(text(), 'Vijuese »')]")
            elif site_type == "punajuaj":
                next_button = driver.find_elements(By.CSS_SELECTOR, "a.next.page-numbers")

            # If there's no "Next" button, stop the scraping process (last page reached)
            if not next_button:
                print("No next button found, stopping...")
                break  

            # Increment the page number to go to the next page
            page += 1
    
    finally:
        # Close the browser once scraping is complete
        driver.quit()

    # Return the scraped data as a Pandas DataFrame
    return pd.DataFrame(all_jobs)
