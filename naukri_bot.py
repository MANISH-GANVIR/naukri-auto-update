from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import os

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

if not EMAIL or not PASSWORD:
    raise RuntimeError("Missing NAUKRI_EMAIL / NAUKRI_PASSWORD secrets")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1366,768")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 40)

def dump_debug(tag: str):
    os.makedirs("debug", exist_ok=True)
    driver.save_screenshot(f"debug/{tag}.png")
    with open(f"debug/{tag}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("DEBUG_URL:", driver.current_url)

def wait_first(locator_list):
    last = None
    for by, sel in locator_list:
        try:
            return wait.until(EC.visibility_of_element_located((by, sel)))
        except Exception as e:
            last = e
    raise last

try:
    driver.get("https://www.naukri.com/nlogin/login")

    # Sometimes overlays/cookie banners appear; try close buttons if present (best-effort)
    for xp in [
        "//button[contains(.,'Accept')]",
        "//button[contains(.,'Got it')]",
        "//div[contains(@class,'cross') or contains(@class,'close')]",
    ]:
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xp))).click()
        except Exception:
            pass

    # Robust email locator fallbacks (DON'T rely on placeholder text)
    email_el = wait_first([
        (By.CSS_SELECTOR, "input#usernameField"),
        (By.CSS_SELECTOR, "input[name='username']"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[contains(@aria-label,'Email') or contains(@aria-label,'email')]"),
    ])
    email_el.clear()
    email_el.send_keys(EMAIL)

    pass_el = wait_first([
        (By.CSS_SELECTOR, "input#passwordField"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.XPATH, "//input[contains(@aria-label,'Password') or contains(@aria-label,'password')]"),
    ])
    pass_el.clear()
    pass_el.send_keys(PASSWORD)

    login_btn = wait_first([
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(.,'Login') or contains(.,'Sign in')]"),
    ])
    login_btn.click()

    time.sleep(5)
    print("AFTER_LOGIN_URL:", driver.current_url)

    # If login didn't land properly, dump debug and fail fast
    if "nlogin" in driver.current_url:
        dump_debug("still_on_login")
        raise RuntimeError("Login seems not completed (still on login page). Possibly UI change / captcha / blocked in headless.")

    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    # Continue popup (best-effort)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Continue')]"))).click()
        time.sleep(2)
    except Exception:
        pass

    # Upload resume (ensure correct path)
    resume_path = os.path.abspath("resume.pdf")
    upload = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    upload.send_keys(resume_path)

    time.sleep(5)
    print("Resume Updated Successfully")

except TimeoutException:
    dump_debug("timeout")
    raise
finally:
    driver.quit()
