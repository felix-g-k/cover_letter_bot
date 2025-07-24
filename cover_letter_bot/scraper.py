from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def close_sign_in_modal(driver):
    """
    Closes the LinkedIn sign-in modal pop-up if it appears. If not found, clicks near the edge of the page to try to dismiss it.
    """
    try:
        # Wait up to 10 seconds for the button to be clickable
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.contextual-sign-in-modal__modal-dismiss"))
        )
        button.click()
        time.sleep(1)
        print("Sign in modal closed.")
    except Exception as e:
        print("Sign in modal not found or not clickable, clicking outside to dismiss.")
        # Try clicking near the edge of the page (e.g., top-left corner)
        try:
            ActionChains(driver).move_by_offset(10, 10).click().perform()
            time.sleep(1)
            print("Clicked outside modal to attempt dismissal.")
        except Exception as click_e:
            print("Failed to click outside modal:", click_e)
        # Optionally, print all button HTMLs for debugging
        # buttons = driver.find_elements(By.TAG_NAME, "button")
        # for btn in buttons:
        #     print(btn.get_attribute("outerHTML"))

def click_show_more_button(driver):
    """
    Clicks the 'Show more' button to expand the full job description if present.
    """
    try:
        # Wait a moment for the button to appear
        time.sleep(1)
        button = driver.find_element(
            "css selector",
            ".show-more-less-html__button--more"
        )
        if button.is_displayed() and button.is_enabled():
            button.click()
            time.sleep(1)  # Wait for content to expand
    except (NoSuchElementException, ElementNotInteractableException):
        print("Show more button not found")
        pass  # Button not present or already clicked

def save_job_description(text: str, output_path: str = "output/job_description.txt"):
    """
    Saves the extracted job description text to the specified output path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def scrape_job_description(url: str) -> str:
    """
    Scrapes and formats the job description from a LinkedIn job listing using Selenium to fetch the page.
    Returns a neatly formatted string with sections: About, Tasks, Benefits, Requirements, Contact.
    Note: Requires ChromeDriver (or another webdriver) to be installed and in PATH.
    """
    # Set up headless Chrome
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for page to load (may need to adjust for slow connections)
        close_sign_in_modal(driver)
        click_show_more_button(driver)
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    job_details = soup.find("div", class_="show-more-less-html__markup")
    print(job_details.prettify())
    if not job_details:
        # Print all IDs present in the HTML
        all_ids = set(tag.get('id') for tag in soup.find_all(attrs={"id": True}))
        print("IDs found in the HTML:")
        for id_val in all_ids:
            print(f"- {id_val}")
        # Print all button class names and IDs
        print("Button class names and IDs found in the HTML:")
        for button in soup.find_all('button'):
            btn_id = button.get('id')
            btn_class = button.get('class')
            if btn_id or btn_class:
                print(f"- id: {btn_id}, class: {btn_class}")
        raise ValueError("Could not find job details section.")

    # General extraction: get all readable text, preserving line breaks
    def extract_all_text(job_details):
        # Use get_text with separator to preserve line breaks
        return job_details.get_text(separator="\n", strip=True)

    formatted = extract_all_text(job_details)
    save_job_description(formatted)
    return formatted

if __name__ == "__main__":
    # Example usage
    #url = input("Enter LinkedIn job URL: ")
    url = r"https://www.linkedin.com/jobs/search/?currentJobId=4267899131&f_C=87192680&geoId=92000000&origin=COMPANY_PAGE_JOBS_CLUSTER_EXPANSION&originToLandingJobPostings=4267899131&trk=d_flagship3_company"
    url = r"https://www.linkedin.com/jobs/view/4239751114/?eBP=CwEAAAGYNij_e89mKeMwunFTW86lx5UKb_FkIcSyNNR3vNbUKqdrHYT5F4WyG4XrqxRkAHNwBv8Kj15-m7ZY0dWwDpONgj0BXPknAQH0ORrCJXEmOgZ5opEDVAUFBDqm9wYuWPpHLtGKVh368xx2DTbzkTiFxqstoxAhmxXSywt59lvqoDObq69WwqUMz0t-7rspMGpWcdIFvdIaqJa2C6yVFZXI_X8PjX-FLbrppO4dNgpLkoCx6hOEmKG4REYaeqpwmTPqw6-fNXG1Ok2khYtZPZlD4bTqswLVRcelseJyWyKrQzb8SeWDFXowrH8FwIKnPcRykqx_9alGk2WvBEKX1v6tCNnYJfFxfQcBJXbSndPRpE7OmgZ1koUZrlsITwLg0Ice3qTzCVlGzE3JGjTBll12uXMFJWZH4pBw5ZDjO2wGz84xg63I1l2yVJnS9lFkloYbeZetbHVbrAI7ryxnCIC9Wmsw7SeAxQWrZ3_d2D1VEp6NARxdbzbMZa-au1AiF9lpTIo&refId=Q%2FwEXNcr9rRHFmtGXdpCUw%3D%3D&trackingId=iQxqqiyMaxV5VSa1MwjKpA%3D%3D&trk=flagship3_jobs_discovery_jymbii"
    job_description = scrape_job_description(url)
    print("\n--- Formatted Job Description ---\n")
    print(job_description)
