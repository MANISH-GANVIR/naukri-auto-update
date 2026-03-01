from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import os

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(3)

    driver.find_element(By.ID,"usernameField").send_keys(EMAIL)
    driver.find_element(By.ID,"passwordField").send_keys(PASSWORD)
    driver.find_element(By.XPATH,"//button[text()='Login']").click()
    time.sleep(5)

    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    upload = driver.find_element(By.XPATH,"//input[@type='file']")
    upload.send_keys("resume.pdf")

    time.sleep(5)
    print("Resume Updated")

finally:
    driver.quit()
