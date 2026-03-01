from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 30)

try:
    # Open Login Page
    driver.get("https://www.naukri.com/nlogin/login")

    # Click Email Login Tab (important for new UI)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Enter your active Email ID"]'))).send_keys(EMAIL)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Enter your password"]'))).send_keys(PASSWORD)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Login")]'))).click()

    time.sleep(5)

    # Go to Profile
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    # Handle Continue popup
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Continue")]'))).click()
        time.sleep(3)
    except:
        pass

    # Upload Resume
    upload = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
    upload.send_keys("resume.pdf")

    time.sleep(5)
    print("Resume Updated Successfully")

finally:
    driver.quit()
