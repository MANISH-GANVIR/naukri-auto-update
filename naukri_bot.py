from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    # Open Login Page
    driver.get("https://www.naukri.com/nlogin/login")

    # Enter Email
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))).send_keys(EMAIL)

    # Enter Password
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))).send_keys(PASSWORD)

    # Click Login
    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()

    time.sleep(5)

    # Open Profile
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    # Handle "Continue" popup if present
    try:
        continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Continue")]')))
        continue_btn.click()
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
