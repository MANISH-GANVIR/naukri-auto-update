from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")
if not EMAIL or not PASSWORD:
    raise RuntimeError("Missing NAUKRI_EMAIL / NAUKRI_PASSWORD secrets")

def dump_debug(driver, tag: str):
    os.makedirs("debug", exist_ok=True)
    driver.save_screenshot(f"debug/{tag}.png")
    with open(f"debug/{tag}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("DEBUG_URL:", driver.current_url)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1366,768")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 50)

try:
    driver.get("https://www.naukri.com/nlogin/login")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(5)

    # If bot protection/captcha page appears, stop with debug
    page_text = driver.page_source.lower()
    if any(x in page_text for x in ["captcha", "verify you are human", "unusual traffic", "robot"]):
        dump_debug(driver, "blocked_or_captcha")
        raise RuntimeError("Blocked/CAPTCHA detected on GitHub-hosted runner IP. Cloud-only run likely not possible reliably.")

    # Robust selectors (best-effort)
    email = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[name='username'], input#usernameField")))
    email.clear()
    email.send_keys(EMAIL)

    pwd = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password'], input#passwordField")))
    pwd.clear()
    pwd.send_keys(PASSWORD)

    btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    btn.click()

    time.sleep(6)
    print("AFTER_LOGIN_URL:", driver.current_url)

    if "nlogin" in driver.current_url:
        dump_debug(driver, "still_on_login")
        raise RuntimeError("Login not completed. Possible OTP/CAPTCHA/UI change.")

    driver.get("https://www.naukri.com/mnjuser/profile")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(4)

    resume_path = os.path.abspath("resume.pdf")
    upload = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    upload.send_keys(resume_path)

    time.sleep(5)
    print("Resume Updated Successfully")

except TimeoutException:
    dump_debug(driver, "timeout")
    raise
finally:
    driver.quit()
