import streamlit as st
import pandas as pd
from io import BytesIO
from scraper_bs import scrape_jobs_from_pages
from scraper_selenium import scrape_all_jobs_selenium

# Streamlit UI
st.title("Job Portal Scraper")
st.write("Enter a job portal URL to scrape job listings and download as CSV/Excel.")

# User input for URL and site type
url = st.text_input("Enter the Job Portal URL:")
site_type = st.selectbox("Select the site type:", ["duapune", "punajuaj"])
use_selenium = st.checkbox("Use Selenium for dynamic content (slower but more reliable for JavaScript-heavy sites)")

if st.button("Scrape Jobs"):
    if url:
        st.write("Scraping data... Please wait.")
        
        try:
            if use_selenium:
                job_data = scrape_all_jobs_selenium(url, site_type)
            else:
                job_data = scrape_jobs_from_pages(url, site_type, start_page=1)

            if not job_data.empty:
                st.success("Data scraped successfully! Download below.")
                if site_type == "duapune":
                    columns = ["Title", "Company", "Location", "Job Type", "Expire"]
                elif site_type == "punajuaj":
                    columns = ["Title", "Company", "Job Type", "Location", "Category", "Language"]
                
                job_df = pd.DataFrame(job_data, columns=columns)
                st.dataframe(job_df)

                # Convert to CSV
                csv_file = job_df.to_csv(index=False).encode('utf-8')

                # Convert to Excel
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    job_df.to_excel(writer, index=False)
                excel_data = excel_buffer.getvalue()

                # Provide download buttons
                st.download_button(label="Download CSV", data=csv_file, file_name="jobs.csv", mime="text/csv")
                st.download_button(label="Download Excel", data=excel_data, file_name="jobs.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.error("No job listings found.")
        except Exception as e:
            st.error(f"Error during scraping: {e}")
    else:
        st.error("Please enter a valid URL.")
